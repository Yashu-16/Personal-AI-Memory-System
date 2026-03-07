"""Tests for authentication endpoints."""

import pytest


def test_register_success(client):
    """A new user can register and receives tokens."""
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "password123", "full_name": "New User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user):
    """Registering with an already-used email returns 409."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
            "full_name": "Duplicate",
        },
    )
    assert response.status_code == 409


def test_login_success(client, test_user):
    """Valid credentials return tokens."""
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client, test_user):
    """Wrong password returns 401."""
    response = client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    """Authenticated request to /me returns user info."""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"


def test_get_me_unauthenticated(client):
    """Request to /me without a token returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
