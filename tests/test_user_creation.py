from fastapi import HTTPException, status
from src.templates.operations import create_user
from unittest.mock import patch, AsyncMock
import pytest


@pytest.mark.asyncio
async def test_create_user_existing():
    with patch("src.your_new_folder.your_module.get_db") as mock_get_db:
        # Simulate finding an existing user
        mock_get_db.return_value.find_one = AsyncMock(
            return_value={"username": "testuser"}
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_user("testuser", "password")

        # Check if the correct exception is raised
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert str(exc_info.value.detail) == "User exist"
