from fastapi import FastAPI
from src.routers.pdf import router as pdf_router
from src.phi_2.router import router as model_route
from src.routers.routers import users, chats, payment

app = FastAPI()

origins = [
    "http://localhost:8000"
    ]

app.include_router(users)
app.include_router(chats)
app.include_router(payment)
app.include_router(pdf_router, prefix="/pdf")
app.include_router(model_route)
