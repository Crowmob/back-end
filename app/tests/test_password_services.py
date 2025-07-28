from app.utils.password import password_services


def test_hash_and_verify_password():
    test_password = "1234"
    hashed_password = password_services.hash_password(test_password)

    assert test_password != hashed_password
    assert password_services.check_password(test_password, hashed_password)
