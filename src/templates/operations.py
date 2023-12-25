import os
import openai
from fastapi import HTTPException
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status


load_dotenv()


def get_db():
    """
    Async connect to database.
    Returns database collection 'users'.
    """
    client = AsyncIOMotorClient(os.environ.get('DATABASE'))
    db = client['Users']
    collection = db['users']
    return collection


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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ви: " + message},
            {"role": "user", "content": ""},
        ],
    )
    reply = response['choices'][0]['message']['content']
    return reply


async def create_chat(user_id):
    """
    Create a new chat in the database for a specific user.
    Args:
        user_id: The ID of the user for whom the chat is being created.
    Returns:
        str: The ID of the created chat.
    """
    collection = get_db()
    try:
        chat = {'user_id': user_id}
        result = await collection['chats'].insert_one(chat)
        return result.inserted_id
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def send_message(chat_id, question, answer):
    """
    Send a message in a specific chat, generating an answer using GPT-3.5-turbo model.
    Args:
        chat_id: The ID of the chat to which the message is being sent.
        question: The question or input message.
        answer: The generated answer for the given question.
    """
    collection = get_db()
    try:
        answer = generate_response_from_model(question)
        message = {'chat_id': chat_id, 'question': question, 'answer': answer}
        await collection['messages'].insert_one(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

async def get_chat_history(chat_id):
    """
    Get the chat history for a specific chat ID.
    Args:
        chat_id: The ID of the chat for which the history is requested.
    Returns:
        list: A formatted list containing chat history with chat ID, questions, and answers.
    """
    collection = get_db()
    try:
        chat_history = await collection['messages'].find({"chat_id": chat_id}).to_list(length=None)
        formatted_history = []
        for message in chat_history:
            formatted_message = {
                "chat_id": message.get("chat_id"),
                "question": message.get("question"),
                "answer": message.get("answer")
            }
            formatted_history.append(formatted_message)
        return formatted_history
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")