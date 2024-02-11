from motor.motor_asyncio import AsyncIOMotorClient

from core.settings import settings

client = AsyncIOMotorClient(settings.db.url)
