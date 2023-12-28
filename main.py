from fastapi import FastAPI

from src.routers.pdf_2 import router as pdf2_router
from src.routers.routers import users, chats

app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.include_router(users)
app.include_router(chats)
app.include_router(pdf2_router, prefix="/pdf")
