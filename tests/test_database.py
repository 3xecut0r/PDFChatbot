from src.utils.get_mongo import get_collection
from unittest.mock import patch, MagicMock


# TODO has to be async, doesn't work
def test_get_collection():
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = 'users_collection_mock'

        collection = await get_collection('users')
        assert collection == 'users_collection_mock'
        mock_client.assert_called_once()  # Check if the client is called


# TODO has to be async, doesn't work
def test_get_chat_data():
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = 'chats_collection_mock'

        collection_chat = await get_collection('chats')
        assert collection_chat == 'chats_collection_mock'
        mock_client.assert_called_once()  # Check if the client is called


# TODO has to be async, doesn't work
def test_get_msg_data():
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = 'messages_collection_mock'

        collection_msg = await get_collection('messages')
        assert collection_msg == 'messages_collection_mock'
        mock_client.assert_called_once()  # Check if the client is called
