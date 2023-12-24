from fastapi import FastAPI, status, UploadFile, File, HTTPException
from src.schemas import HealthCheck
from fastapi.responses import HTMLResponse
from typing import List
import openai
from src.routers.routers import users
app = FastAPI()
origins = [
    "http://localhost:8000"
    ]
app.include_router(users)


# Встановлення вашого API ключа
api_key = "YOUR_API_KEY"
openai.api_key = api_key
history = []

# Функція для взаємодії з Large Language Model
def generate_response_from_model(message: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ви: " + message},
            {"role": "user", "content": ""},
        ],
    )
    reply = response['choices'][0]['message']['content']
    return reply


@app.post("/chat/")
async def chat_with_model(message: str):
    global history
    history.append(message)
    response = generate_response_from_model(message)
    return {"response": response}


@app.get("/chat_history/", response_class=HTMLResponse)
async def show_chat_history():
    global history
    html_content = "<h2>Історія чату:</h2>"
    for idx, message in enumerate(history, start=1):
        html_content += f"<p><strong>Повідомлення {idx}:</strong> {message}</p>"

    return html_content