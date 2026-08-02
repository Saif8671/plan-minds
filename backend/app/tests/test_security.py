from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


def test_password_hashing():
    hashed = hash_password("securepassword123")
    assert verify_password("securepassword123", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_tokens():
    token = create_access_token("user-123")
    assert verify_token(token, expected_type="access") == "user-123"
    assert verify_token(token, expected_type="refresh") is None
