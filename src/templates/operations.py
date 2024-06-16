from fastapi import HTTPException
from fastapi.responses import JSONResponse
import requests
from requests.auth import HTTPBasicAuth
from openai import OpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status
from docx import Document
import pdfplumber
import csv
import logging

from src.conf.config import settings
from src.base_model.basemodel import BASEMODEL
from src.utils.get_mongo import get_collection

USERNAME = settings.username_mongo
PASSWORD = settings.password_mongo
CLIENT = settings.paypal_client
SECRET = settings.paypal_secret

model_basic = 'basemodel'
model_premium = 'gpt-3.5-turbo'


async def create_user(name, password):
    """
    Function those create new user object in database 'Users'.
    name: str
    password: str
    """
    collection = await get_collection('users')
    try:
        existing_user = await collection.find_one({'username': name})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exist')
        else:
            await collection.insert_one({'username': name, 'password': password, 'premium': False})
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail='Internal Server Error')


def generate_response_from_model(message: str) -> str:
    """
    Generate a response using the GPT-3.5-turbo model based on the provided message/question.
    Args:
        message: The input message or question.
    Returns:
        str: The generated response from the GPT-3.5-turbo model.
    """
    response = OpenAI(api_key=settings.openai_api_key).chat.completions.create(
        model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': message}, {'role': 'system', 'content': ''}]
    )
    return response.choices[0].message.content


async def create_chat(user_id):
    """
    Create a new chat in the database for a specific user.
    Args:
        user_id: The ID of the user for whom the chat is being created.
    Returns:
        str: The ID of the created chat.
    """
    collection_chat = await get_collection('chats')
    try:
        chat = {'user_id': user_id}
        result = await collection_chat.insert_one(chat)
        return result.inserted_id
    except Exception:
        raise HTTPException(status_code=500, detail='Internal Server Error')


async def create_message(chat_id: str, question: str, model: str = 'model_basic', content: str = None):
    """
    Send a message in a specific chat, generating an answer using GPT-3.5-turbo model.
    Args:
        content:
        model:
        chat_id: The ID of the chat to which the message is being sent.
        question: The question or input message.
    """
    collection_msg = await get_collection('messages')
    try:
        if model == 'model_premium':
            if content:
                question_with_file = f'Question:{question} File to analize:{content[:3500]}'
                answer = generate_response_from_model(question_with_file)
            else:
                answer = generate_response_from_model(question)
        elif model == 'model_basic':
            if content:
                answer = await BASEMODEL.answer(f'Question:{question} \n\n {content}')
            else:
                answer = await BASEMODEL.answer(question)
        else:
            answer = 'Select model!'

        message = {'chat_id': chat_id, 'question': question, 'answer': answer, 'model': model}
        await collection_msg.insert_one(message)
        return answer
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail='Internal Server Error')


async def get_chat_history(chat_id):
    """
    Get the chat history for a specific chat ID.
    Args:
        chat_id: The ID of the chat for which the history is requested.
    Returns:
        list: A formatted list containing chat history with chat ID, questions, and answers.
    """
    collection_msg = await get_collection('messages')
    try:
        chat_history = await collection_msg.find({'chat_id': chat_id}).to_list(length=None)
        formatted_history = []
        for message in chat_history:
            formatted_message = {'question': message.get('question'), 'answer': message.get('answer')}
            formatted_history.append(formatted_message)
        return formatted_history
    except Exception:
        raise HTTPException(status_code=500, detail='Internal Server Error')


def size_warning_response():
    return JSONResponse(
        content={
            'warning': 'File size exceeds 4000 symbols. Please reduce the file size or abort the operation.',
            'action_required': True,
        },
        status_code=200,
    )


def extract_text_from_pdf(pdf_content):
    text = ''
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()
    return text


def extract_data_from_csv(csv_content):
    reader = csv.DictReader(csv_content)
    return [row for row in reader]


def extract_text_from_docx(doc_content):
    doc = Document(doc_content)
    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])


async def get_payment(user):
    """
    Request method. We send our PayPal credentials to PayPal service.
    If request status code = 201, we get json objects with links for redirect our client
    on a payment page.
    Else response return bad request status code.
    Args:
        user: username --> str, for MongoDB collection['Users'].find_one({'username': user})

    Returns: redirect link --> str. or status code (400. bad request)
    """
    collection = await get_collection('users')
    auth = HTTPBasicAuth(CLIENT, SECRET)
    headers = {'Content-Type': 'application/json'}
    payload = {
        'intent': 'sale',
        'payer': {'payment_method': 'paypal'},
        'transactions': [{'amount': {'total': '1.00', 'currency': 'USD'}}],
        'redirect_urls': {
            'return_url': 'http://16.171.144.42:8000/payment/execute',
            'cancel_url': 'http://16.171.144.42:8000/payment/cancel',
        },
    }

    response = requests.post(
        'https://api.sandbox.paypal.com/v1/payments/payment', json=payload, auth=auth, headers=headers
    )
    if response.status_code == 201:
        pay = response.json().get('links')[1].get('href')
        token = pay.split('token=')[-1]
        collection.update_one({'username': user}, {'$set': {'token': token}})
        return pay
    else:
        return HTTPException(status_code=400, detail='Bad request')


async def execute_paypal_payment(payment_id, payer_id, user):
    """
    Checking response if pay was accepted.
    Args:
        payment_id: str
        payer_id: srt
        user: username --> str, for MongoDB collection['Users'].find_one({'username': user})

    Returns: True if all good. False if pay was not accepted.
    """
    execute_url = f'https://api.sandbox.paypal.com/v1/payments/payment/{payment_id}/execute'
    response = requests.post(
        execute_url,
        json={'payer_id': payer_id},
        auth=HTTPBasicAuth(CLIENT, SECRET),
        headers={'Content-Type': 'application/json'},
    )
    if response.status_code == 200:
        collection = await get_collection('users')
        collection.update_one({'username': user}, {'$set': {'premium': True}})
        return True
    else:
        logging.error(f'Payment execution failed:\n{response.text}')
        return False
