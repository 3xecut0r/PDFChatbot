from fastapi import FastAPI

from src.routers.routers import router
from src.routers.routers import users, chats, main
from starlette.staticfiles import StaticFiles
app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main)
app.include_router(users)
app.include_router(chats)
app.include_router(router, prefix="/pdf")
