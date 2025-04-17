from uuid import UUID

from app.models.user_model import UserRole
from app.services.user_service import UserService
from app.utils.nickname_gen import generate_nickname


async def test_create_user_with_valid_data(db_session):
    """
    Ensuring that UUID is generated
    """
    user_data = {
        "nickname": generate_nickname(),
        "email": "valid_user@example.com",
        "password": "ValidPassword123!",
        "role": UserRole.ADMIN.name
    }
    user = await UserService._create_user_in_db(db_session, user_data)
    assert user is not None
    assert user.email == user_data["email"]
    assert isinstance(user.id, UUID)
