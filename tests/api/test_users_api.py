import pytest

from tests.factories import TEST_PASSWORD, auth_headers, make_user
from users.users_schemas import UserRole

pytestmark = pytest.mark.api

REGISTER_URL = "/users/auth/register"
LOGIN_URL = "/users/auth/login"


def register(client, login="newbie", email="newbie@example.com", password="password123"):
    return client.post(REGISTER_URL, json={"login": login, "email": email, "password": password})


def role_url(user_id: int) -> str:
    return f"/users/{user_id}/role"


def test_register_returns_201(client):
    response = register(client)

    assert response.status_code == 201
    assert response.json()["login"] == "newbie"
    assert "hashed_password" not in response.json()


def test_register_duplicate_login_returns_409(client, user):
    assert register(client, login=user.login).status_code == 409


def test_register_duplicate_email_returns_409(client, user):
    assert register(client, email=user.email).status_code == 409


def test_register_login_of_one_user_and_email_of_another_returns_409(client, user, other_user):
    response = register(client, login=user.login, email=other_user.email)

    assert response.status_code == 409


def test_register_login_with_at_sign_returns_422(client):
    assert register(client, login="new@bie").status_code == 422


@pytest.mark.parametrize("identifier", ["user", "user@example.com"])
def test_login_by_login_or_email_returns_token(client, user, identifier):
    response = client.post(LOGIN_URL, json={"login_or_email": identifier, "password": TEST_PASSWORD})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_wrong_password_and_unknown_login_look_the_same(client, user):
    wrong_password = client.post(LOGIN_URL, json={"login_or_email": user.login, "password": "wrong-pass"})
    unknown_login = client.post(LOGIN_URL, json={"login_or_email": "nobody", "password": "wrong-pass"})

    assert wrong_password.status_code == unknown_login.status_code == 401
    assert wrong_password.json() == unknown_login.json()


def test_admin_changes_role_of_other_user(client, admin, user):
    response = client.patch(role_url(user.id), json={"role": "admin"}, headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_can_demote_other_admin(client, db, admin):
    other_admin = make_user(db, "second_admin", UserRole.ADMIN)

    response = client.patch(role_url(other_admin.id), json={"role": "user"}, headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json()["role"] == "user"


def test_admin_cannot_change_own_role(client, admin):
    response = client.patch(role_url(admin.id), json={"role": "user"}, headers=auth_headers(admin))

    assert response.status_code == 403


def test_change_role_of_missing_user_returns_404(client, admin):
    response = client.patch(role_url(999_999), json={"role": "user"}, headers=auth_headers(admin))

    assert response.status_code == 404


def test_regular_user_cannot_change_roles(client, user, other_user):
    response = client.patch(role_url(other_user.id), json={"role": "admin"}, headers=auth_headers(user))

    assert response.status_code == 403
