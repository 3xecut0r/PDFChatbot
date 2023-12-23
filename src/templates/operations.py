import os

from fastapi import HTTPException
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status


load_dotenv()


def get_db():
    """
    Async connect to database.
    Returns database collection 'users'.
    """
    client = AsyncIOMotorClient(os.environ.get('DATABASE'))
    db = client['Users']
    collection = db['users']
    return collection


async def create_user(name, password):
    """Function those create new user object in database 'Users'.
        name: str
        password: str
    """
    collection = get_db()
    try:
        existing_user = await collection.find_one({"username": name})
        print(existing_user)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exist")
        else:
            await collection.insert_one({'username': name, 'password': password})
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
