from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
import secrets
from time import sleep
from typing import Optional, Dict, List

import backoff
from asyncpg.exceptions import InvalidCachedStatementError
from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError, NotSupportedError, InternalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_settings
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID
from app.models.user_model import UserRole
from app.celery.tasks import (
    verify_email_task,
    account_locked_task,
    account_unlocked_task,
    role_upgrade_task,
    professional_status_upgrade_task
)
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    @backoff.on_exception(
        backoff.expo,
        (NotSupportedError, InternalError),
        max_tries=2,
        jitter=None,
    )
    async def _backoff_query(cls, session: AsyncSession, query):
        try:
            logger.error(f"Backoff before committing query: {query}")
            result = await session.execute(query)
            await session.commit()
            logger.error("Backoff after committing query:")
            print(f"Rusult: {result}")
        except (NotSupportedError, InternalError) as e:
            logger.error(f"Error during query execution: {e}, backing off and retrying.")
            await session.rollback()
            sleep(1)
            raise
        return result

    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        """
        Executes & commits.  If the 'cached statement invalid'
        error fires, backoff will rollback and retry once.
        """
        try:
            logger.error("Executing query:")
            result = await cls._backoff_query(session, query)
            logger.error("Query executed successfully.")
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None
        return result

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str]) -> Optional[User]:
        try:
            new_user = await cls._create_user_in_db(session, user_data)

            if not new_user.email_verified:
                new_user.verification_token = generate_verification_token()
                await session.commit()
                verify_email_task.delay(new_user.id)

            return new_user

        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None
        except ValueError as e:
            logger.error(f"ValueError during user creation: {e}")
            return None


    @classmethod
    async def _create_user_in_db(cls, session: AsyncSession, user_data: Dict[str, str]) -> User:
        validated_data = UserCreate(**user_data).model_dump()

        if await cls.get_by_email(session, validated_data['email']):
            raise ValueError("User with given email already exists.")

        validated_data['hashed_password'] = hash_password(validated_data.pop('password'))

        new_user = User(**validated_data)

        # Generate unique nickname
        new_nickname = generate_nickname()
        while await cls.get_by_nickname(session, new_nickname):
            new_nickname = generate_nickname()
        new_user.nickname = new_nickname

        user_count = await cls.count(session)
        new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS
        new_user.email_verified = new_user.role == UserRole.ADMIN

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user

    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            # validated_data = UserUpdate(**update_data).dict(exclude_unset=True)
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)

            if 'password' in validated_data:
                validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            query = update(User).where(User.id == user_id).values(**validated_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)
            updated_user = await cls.get_by_id(session, user_id)
            logger.error(f"Updated user: {updated_user}")
            if updated_user:
                session.refresh(updated_user)  # Explicitly refresh the updated user object
                logger.error(f"User {user_id} updated successfully.")
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update attempt.")
            return None
        except Exception as e:  # Broad exception handling for debugging
            logger.error(f"Error during user update: {e}")
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str]) -> Optional[User]:
        return await cls.create(session, user_data)


    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await cls.get_by_email(session, email)
        if user:
            if user.email_verified is False:
                return None
            if user.is_locked:
                return None
            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                    # Schedule account locked notification
                    account_locked_task.delay(user.id)
                session.add(user)
                await session.commit()
        return None

    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        user = await cls.get_by_email(session, email)
        return user.is_locked if user else False


    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            was_locked = user.is_locked
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0  # Resetting failed login attempts
            user.is_locked = False  # Unlocking the user account, if locked
            session.add(user)
            await session.commit()
            # If the account was locked and is now unlocked, send notification
            if was_locked:
                account_unlocked_task.delay(user.id)
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.verification_token == token:
            user.email_verified = True
            user.verification_token = None  # Clear the token once used
            old_role = user.role
            user.role = UserRole.AUTHENTICATED
            session.add(user)
            await session.commit()
            # If the role was upgraded, send notification
            if old_role != UserRole.AUTHENTICATED:
                role_upgrade_task.delay(user.id, UserRole.AUTHENTICATED.name)
            return True
        return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of users in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of users.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        count = result.scalar()
        return count

    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0  # Optionally reset failed login attempts
            session.add(user)
            await session.commit()
            # Schedule account unlocked notification
            account_unlocked_task.delay(user.id)
            return True
        return False

    @classmethod
    async def upgrade_user_role(cls, session: AsyncSession, user_id: UUID, new_role: UserRole) -> bool:
        """
        Upgrade a user's role to a new role.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to upgrade.
        :param new_role: The new role to assign to the user.
        :return: True if the role was upgraded successfully, False otherwise.
        """
        user = await cls.get_by_id(session, user_id)
        if user and user.role != new_role:
            old_role = user.role
            user.role = new_role
            session.add(user)
            await session.commit()
            # Schedule role upgrade notification
            role_upgrade_task.delay(user.id, new_role.name)
            logger.info(f"User {user_id} role upgraded from {old_role.name} to {new_role.name}")
            return True
        return False

    @classmethod
    async def upgrade_professional_status(cls, session: AsyncSession, user_id: UUID) -> bool:
        """
        Upgrade a user's professional status.

        :param session: The AsyncSession instance for database access.
        :param user_id: The ID of the user to upgrade.
        :return: True if the professional status was upgraded successfully, False otherwise.
        """
        user = await cls.get_by_id(session, user_id)
        if user and not user.is_professional:
            user.update_professional_status(True)
            session.add(user)
            await session.commit()
            # Schedule professional status upgrade notification
            professional_status_upgrade_task.delay(user.id)
            logger.info(f"User {user_id} professional status upgraded")
            return True
        return False
