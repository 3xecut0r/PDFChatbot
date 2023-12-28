from motor.motor_asyncio import AsyncIOMotorClient

from src.conf.config import settings  


USERNAME = settings.username_mongo
PASSWORD = settings.password_mongo


async def get_mongodb():
    client = AsyncIOMotorClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@pdfchatbot.zkaopxh.mongodb.net/?retryWrites=true&w=majority')
    return client.storage
