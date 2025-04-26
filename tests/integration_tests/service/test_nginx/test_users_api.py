"""
tests/integration/service_http/test_user_routes_via_nginx.py
Purpose
-------
Verify that Nginx is correctly forwarding requests to the FastAPI
backend and that auth headers / bodies survive the hop.

Assumptions
-----------
* docker-compose up has already started the full stack and Nginx is
  reachable on http://localhost:80 (or the port you mapped).
* Your existing conftest.py already provides: admin_user, admin_token,
  manager_token, user_token, verified_user, unverified_user,
  locked_user, users_with_same_role_50_users, etc.
"""

import pytest
import httpx
from urllib.parse import urlencode

BASE_URL = "http://nginx"          # change if you mapped another port
TIMEOUT  = 10                          # keep low to fail fast on bad proxy


@pytest.fixture
async def nginx_client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        yield client


@pytest.mark.asyncio
async def test_retrieve_user_access_denied_via_nginx(
        nginx_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    r = await nginx_client.get(f"/users/{verified_user.id}", headers=headers)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_retrieve_user_access_allowed_via_nginx(
        nginx_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = await nginx_client.get(f"/users/{admin_user.id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == str(admin_user.id)


@pytest.mark.asyncio
async def test_update_user_email_denied_via_nginx(
        nginx_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"email": f"updated_{verified_user.id}@example.com"}
    r = await nginx_client.put(f"/users/{verified_user.id}",
                               json=payload, headers=headers)
    assert r.status_code == 403


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Issue with database caching")
async def test_update_user_email_allowed_via_nginx(
        nginx_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"email": f"updated_{admin_user.id}@example.com"}
    r = await nginx_client.put(f"/users/{admin_user.id}",
                               json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == payload["email"]


@pytest.mark.asyncio
async def test_login_success_via_nginx(nginx_client, verified_user):
    data = urlencode({"username": verified_user.email,
                      "password": "MySuperPassword$1234"})
    r = await nginx_client.post("/login/",
                                content=data,
                                headers={"Content-Type":
                                         "application/x-www-form-urlencoded"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("token_type") == "bearer"
    assert "access_token" in body


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Issue with database caching")
async def test_login_locked_user_via_nginx(nginx_client, locked_user):
    data = urlencode({"username": locked_user.email,
                      "password": "MySuperPassword$1234"})
    r = await nginx_client.post("/login/",
                                content=data,
                                headers={"Content-Type":
                                         "application/x-www-form-urlencoded"})
    print(r.json())
    assert r.status_code == 400
    assert "Account locked" in r.json().get("detail", "")



@pytest.mark.asyncio
async def test_list_users_as_admin_via_nginx(nginx_client, admin_token):
    r = await nginx_client.get("/users/",
                               headers={"Authorization":
                                        f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert "items" in r.json()


@pytest.mark.asyncio
async def test_list_users_unauthorized_via_nginx(nginx_client, user_token):
    r = await nginx_client.get("/users/",
                               headers={"Authorization":
                                        f"Bearer {user_token}"})
    assert r.status_code == 403
