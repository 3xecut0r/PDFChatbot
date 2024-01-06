from openai import OpenAI
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status

from src.conf.config import settings

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from docx import Document
import pdfplumber
import csv

from src.utils.get_mongo import get_mongodb


USERNAME = settings.username_mongo
PASSWORD = settings.password_mongo

def get_db():
    """
    Async connect to database.
    Returns database collection 'users'.
    """
    client = AsyncIOMotorClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@pdfchatbot.zkaopxh.mongodb.net/?retryWrites=true&w=majority')
    db = client['Users']
    collection = db['users']
    return collection

  
def get_chat_data():
    """
    Async connect to database.
    Returns database collection 'chats'.
    """
    client = AsyncIOMotorClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@pdfchatbot.zkaopxh.mongodb.net/?retryWrites=true&w=majority')
    db = client['Users']
    collection_chat = db['chats']
    return collection_chat
    

def get_msg_data():
    """
    Async connect to database.
    Returns database collection 'messages'.
    """
    client = AsyncIOMotorClient(f'mongodb+srv://{USERNAME}:{PASSWORD}@pdfchatbot.zkaopxh.mongodb.net/?retryWrites=true&w=majority')
    db = client['Users']
    collection_msg = db['messages']
    return collection_msg
    

async def create_user(name, password):
    """Function those create new user object in database 'Users'.
        name: str
        password: str
    """
    collection = get_db()
    try:
        existing_user = await collection.find_one({"username": name})
        print(existing_user)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exist")
        else:
            await collection.insert_one({'username': name, 'password': password})
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def generate_response_from_model(message: str) -> str:
    """
    Generate a response using the GPT-3.5-turbo model based on the provided message/question.
    Args:
        message: The input message or question.
    Returns:
        str: The generated response from the GPT-3.5-turbo model.
    """
    client = OpenAI(
        api_key=settings.openai_api_key
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
            {"role": "system", "content": ""},
        ],
    )
    reply = response.choices[0].message.content
    return reply


async def create_chat(user_id):
    """
    Create a new chat in the database for a specific user.
    Args:
        user_id: The ID of the user for whom the chat is being created.
    Returns:
        str: The ID of the created chat.
    """
    collection_chat = get_chat_data()
    try:
        chat = {'user_id': user_id}
        result = await collection_chat.insert_one(chat)
        return result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def create_message(chat_id, question):
    """
    Send a message in a specific chat, generating an answer using GPT-3.5-turbo model.
    Args:
        chat_id: The ID of the chat to which the message is being sent.
        question: The question or input message.
        answer: The generated answer for the given question.
    """
    collection_msg = get_msg_data()
    try:
        answer = generate_response_from_model(question)
        message = {'chat_id': chat_id, 'question': question, 'answer': answer}
        await collection_msg.insert_one(message)
        return answer
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

async def get_chat_history(chat_id):
    """
    Get the chat history for a specific chat ID.
    Args:
        chat_id: The ID of the chat for which the history is requested.
    Returns:
        list: A formatted list containing chat history with chat ID, questions, and answers.
    """
    collection_msg = get_msg_data()
    try:
        chat_history = await collection_msg.find({"chat_id": chat_id}).to_list(length=None)
        formatted_history = []
        for message in chat_history:
            formatted_message = {
                "question": message.get("question"),
                "answer": message.get("answer")
            }
            formatted_history.append(formatted_message)
        return formatted_history
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


def size_warning_response():
    return JSONResponse(
        content={
            "warning": "File size exceeds 4000 symbols. Please reduce the file size or abort the operation.",
            "action_required": True,
        },
        status_code=200,
    )


def extract_text_from_pdf(pdf_content):
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()
    return text


def extract_data_from_csv(csv_content):
    reader = csv.DictReader(csv_content)
    data = [row for row in reader]
    return data


def extract_text_from_docx(doc_content):
    doc = Document(doc_content)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])