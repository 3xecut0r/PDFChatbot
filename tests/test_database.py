from src.templates.operations import get_db, get_chat_data, get_msg_data
from unittest.mock import patch, MagicMock


def test_get_db():
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = "users_collection_mock"

        collection = get_db()
        assert collection == "users_collection_mock"
        mock_client.assert_called_once()  # Check if the client is called


def test_get_chat_data():
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = "chats_collection_mock"

        collection_chat = get_chat_data()
        assert collection_chat == "chats_collection_mock"
        mock_client.assert_called_once()  # Check if the client is called


def test_get_msg_data():
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = "messages_collection_mock"

        collection_msg = get_msg_data()
        assert collection_msg == "messages_collection_mock"
        mock_client.assert_called_once()  # Check if the client is called
