from fastapi import FastAPI, status
from src.schemas import HealthCheck
from src.routers.routers import users
app = FastAPI()
origins = [
    "http://localhost:8000"
    ]
app.include_router(users)
app.include_router(pdf.router, prefix="/pdf")

