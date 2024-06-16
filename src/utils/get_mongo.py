from motor.motor_asyncio import AsyncIOMotorClient

from src.conf.config import settings


# TODO: redesign the logic of the methods, get rid of duplication
async def get_mongodb(database_name: str = 'storage'):
    client = AsyncIOMotorClient(settings.mongo_url)
    return client[database_name]


async def get_collection(collection_name: str, database_name: str = 'Users'):
    database = await get_mongodb(database_name)
    return database[collection_name]


async def get_mongodb_chat_history():
    client = AsyncIOMotorClient(settings.mongo_url)
    return client['Users']
