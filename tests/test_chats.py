from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)


def test_create_chat_route():
    test_user_id = "12345"  # Example user ID
    test_chat_id = "54321"  # Example chat ID to be returned by the mocked create_chat

    # Mock get_current_user dependency
    with patch("myapp.your_module.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = {"_id": test_user_id}

        # Mock create_chat function
        with patch("myapp.your_module.create_chat") as mock_create_chat:
            mock_create_chat.return_value = test_chat_id

            response = client.post("/chats/")
            assert response.status_code == 200
            assert response.json() == {
                "message": "Chat created successfully!",
                "chat_id": test_chat_id,
            }


def test_send_question_route():
    test_user_id = "12345"
    test_chat_id = "54321"
    test_question = "How do I test my API?"
    test_answer = (
        "Just like this!"  # Example answer to be returned by the mocked create_message
    )

    # Mock get_current_user dependency
    with patch("myapp.your_module.get_current_user") as mock_get_current_user:
        mock_get_current_user.return_value = {"_id": test_user_id}

        # Mock create_message function
        with patch("myapp.your_module.create_message") as mock_create_message:
            mock_create_message.return_value = test_answer

            response = client.post(
                f"/chats/{test_chat_id}/send_question", json={"question": test_question}
            )
            assert response.status_code == 200
            assert response.json() == {"answer": test_answer}


def test_show_chat_history_exists():
    test_user_id = "12345"
    test_chat_id = "54321"
    mock_chat_history = [
        {"message": "Hello", "sender": "user1"},
        {"message": "Hi", "sender": "user2"},
    ]

    with patch("myapp.your_module.get_current_user") as mock_user, patch(
        "myapp.your_module.get_chat_history"
    ) as mock_history:
        mock_user.return_value = {"_id": test_user_id}
        mock_history.return_value = mock_chat_history

        response = client.get(f"/chats/{test_chat_id}/history")
        assert response.status_code == 200
        assert response.json() == {"chat_history": mock_chat_history}


def test_show_chat_history_not_exists():
    test_user_id = "12345"
    test_chat_id = "54321"

    with patch("myapp.your_module.get_current_user") as mock_user, patch(
        "myapp.your_module.get_chat_history"
    ) as mock_history:
        mock_user.return_value = {"_id": test_user_id}
        mock_history.return_value = None

        response = client.get(f"/chats/{test_chat_id}/history")
        assert response.status_code == 200
        assert response.json() == {"message": "No chat history found for this chat_id"}
