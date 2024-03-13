from httpx import AsyncClient
from http import HTTPStatus

import pytest

from .conftest import reverse
from routes.users import show_users, registration, patch_user, show_user, delete_user
from routes.auth import login_user, logout_user, refresh_user_token, check_auth


class TestAuth:
    @pytest.mark.asyncio
    async def test_show_empty_users_list(self, client: AsyncClient, cache_operations):
        response = await client.get(reverse(show_users))
        assert response.status_code == HTTPStatus.OK
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_show_empty_user_list(self, client: AsyncClient, cache_operations):
        response = await client.get(reverse(show_user, user_id=""))
        assert response.status_code == HTTPStatus.OK
        assert response.json() == []

    @pytest.mark.parametrize("request_body", [({
        "login": "string",
        "password": "string",
        "email": "user@example.com",
        "phone_number": "string",
        "is_verified": False
    })])
    async def test_register_with_wrong_phone_for_auth(self, client: AsyncClient, request_body, cache_operations):
        response = await client.post(reverse(show_users), json=request_body)
        assert response.status_code == 422

    @pytest.mark.parametrize("request_body", [({
        "login": "string",
        "password": "string",
        "email": "user@example.com",
        "phone_number": "89958999645",
        "is_verified": False
    })])
    async def test_register_for_auth(self, client: AsyncClient, request_body, saved_data, cache_operations):
        response = await client.post(reverse(registration), json=request_body)
        assert response.status_code == HTTPStatus.OK
        assert "id" in response.json()
        assert response.json()["login"] == "string"
        assert response.json()["email"] == "user@example.com"
        assert response.json()["phone_number"] == "89958999645"
        saved_data["user"] = response.json()

    @pytest.mark.parametrize("request_body", [({"login": "string", "password": "string"})])
    async def test_login_user(self, client: AsyncClient, request_body, saved_data, cache_operations):
        response = await client.post(reverse(login_user), json=request_body)
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        saved_data["auth"] = response.json()

    @pytest.mark.asyncio
    async def test_check_auth(self, client: AsyncClient, saved_data, cache_operations):
        auth = saved_data["auth"]
        response = await client.get(reverse(check_auth), headers={"Authorization": f"Bearer {auth["refresh_token"]}"})
        assert response.status_code == HTTPStatus.OK
        assert "id" in response.json()

    @pytest.mark.asyncio
    async def test_refresh_user_token(self, client: AsyncClient, saved_data, cache_operations):
        auth = saved_data["auth"]
        response = await client.get(reverse(refresh_user_token), headers={"Authorization": f"Bearer {auth["refresh_token"]}"})
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
        saved_data["auth"] = response.json()

    @pytest.mark.asyncio
    async def test_logout_user(self, client: AsyncClient, saved_data, cache_operations):
        auth = saved_data["auth"]
        response = await client.post(reverse(logout_user), headers={"Authorization": f"Bearer {auth["refresh_token"]}"})
        assert response.status_code == HTTPStatus.OK
        assert "id" in response.json()
        assert "token" in response.json()
        assert response.json()["token"] == ""
        saved_data["auth"] = response.json()
