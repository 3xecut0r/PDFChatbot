from fastapi.testclient import TestClient
from main import app

from src.schemas import UserModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# from unittest.mock import patch

client = TestClient(app)


TEST_DATABASE_URL = 'sqlite:///./test.db'  # Update this to your test database URL
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def test_user_signup():
    response = client.post(
        '/users/signup', json={'username': 'testuser', 'password': 'testpassword'}
    )
    assert response.status_code == 201
    assert response.json() == 'Created!'

    # Additional assertions to check if the user is created in the database
    with next(get_test_db()) as db:
        user = db.query(UserModel).filter(UserModel.username == 'testuser').first()
        assert user is not None
        assert user.username == 'testuser'

    # Clean up: delete the test user after the test (optional)
    with next(get_test_db()) as db:
        db.delete(user)
        db.commit()


def test_login_success():
    # Assuming 'testuser' is a valid user in test database
    response = client.post(
        '/users/signin', data={'username': 'testuser', 'password': 'testpassword'}
    )
    assert response.status_code == 200
    assert 'access_token' in response.json()


def test_login_invalid_username():
    response = client.post(
        '/users/signin',
        data={'username': 'nonexistentuser', 'password': 'testpassword'},
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username'


def test_login_invalid_password():
    response = client.post(
        '/users/signin', data={'username': 'testuser', 'password': 'wrongpassword'}
    )
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid password'
