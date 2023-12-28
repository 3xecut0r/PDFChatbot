from fastapi import FastAPI

from src.routers import pdf
from src.routers.routers import users, chats

app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.include_router(users)
app.include_router(chats)
app.include_router(pdf.router, prefix="/pdf")
