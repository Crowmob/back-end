import pytest
from app.services.user_service import create_user

def test_create_user_function():
    user = create_user("crowmob", "12345678")
    assert user["username"] == "crowmob"
    assert user["password"] == "12345678"