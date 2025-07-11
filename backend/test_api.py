#!/usr/bin/env python3
"""
Test script for Smart Locker API endpoints
"""
import json

import pytest
import requests

BASE_URL = "http://localhost:5050"


@pytest.fixture(scope="module")
def admin_token():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    return response.json()["token"]


def test_login():
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_stats(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "totalUsers" in data
    assert "totalItems" in data
    assert "totalLockers" in data
    assert "activeBorrows" in data


def test_users(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_items(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/items", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_lockers(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/lockers", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_logs(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/logs", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    print("🧪 Testing Smart Locker API...")
    print("=" * 50)

    # Test login first
    admin_token = admin_token()

    # Test other endpoints
    test_stats(admin_token)
    test_users(admin_token)
    test_items(admin_token)
    test_lockers(admin_token)
    test_logs(admin_token)

    print("\n" + "=" * 50)
    print("API testing complete!")
