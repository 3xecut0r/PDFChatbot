from fastapi import FastAPI
import os

from src.phi_2.router import router as model_route
from src.routers.routers import users, chats, payment
from src.base_model.routers import base

from src.routers.routers import router as pdf_router
from src.routers.routers import users, chats, main
from starlette.staticfiles import StaticFiles

app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.mount("/static", StaticFiles(directory="static"), name="static")

commandline_args = os.environ.get('COMMANDLINE_ARGS', "--skip-torch-cuda-test --no-half")

app.include_router(main)
app.include_router(users)
app.include_router(chats)
app.include_router(payment)
app.include_router(model_route)
app.include_router(pdf_router, prefix="/pdf")
app.include_router(base)
