from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import io

client = TestClient(app)


def test_upload_file():
    test_file_content = b"Test content"
    test_file_name = "test.txt"
    test_file_type = "text/plain"

    # Mock the file upload
    test_file = MagicMock()
    test_file.file.read.return_value = test_file_content
    test_file.filename = test_file_name
    test_file.content_type = test_file_type

    # Mock MongoDB insert_one
    with patch("myapp.your_module.get_mongodb") as mock_mongo:
        mock_collection = MagicMock()
        mock_mongo.return_value = {"files": mock_collection}
        mock_collection.insert_one.return_value.inserted_id = "mock_id"

        response = client.post(
            "/files/upload/",
            files={
                "file": (test_file_name, io.BytesIO(test_file_content), test_file_type)
            },
        )
        assert response.status_code == 200
        assert response.json() == {"id": "mock_id", "name": test_file_name}
