from bson import ObjectId
from starlette.responses import FileResponse
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from io import BytesIO, StringIO
import logging

from src.schemas import UserModel, MessageModel
from src.templates.auth import Hash, create_access_token, get_current_user
from src.templates.operations import create_user, get_payment, execute_paypal_payment
from src.templates.operations import create_chat, create_message, get_chat_history
from src.templates.operations import size_warning_response, extract_text_from_pdf, extract_data_from_csv
from src.templates.operations import extract_text_from_docx
from src.utils.get_mongo import get_mongodb, get_collection


main = APIRouter(prefix='/main', tags=['main'])
users = APIRouter(prefix='/users', tags=['users'])
chats = APIRouter(prefix='/chats', tags=['chats'])
files = APIRouter(prefix='/files', tags=['files'])
payment = APIRouter(prefix='/payment', tags=['payment'])

hash_handler = Hash()


@users.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: UserModel):
    """
    User registration.
    Args:
        user: BaseModel object with 2 params(username: str, password: str)
    Returns: Created!
    """
    name = user.username
    password = user.password
    await create_user(name, password=hash_handler.get_password_hash(password))
    return 'Created!'


@users.post('/signin')
async def login(body: OAuth2PasswordRequestForm = Depends()):
    """
    Sign in function.
    Args:
        body: OAuth2PasswordRequestForm.
    Returns: user access token.
    """
    try:
        collection = await get_collection('users')
        try:
            user = await collection.find_one({'username': body.username})
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username')
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username')
        if not hash_handler.verify_password(body.password, user['password']):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')

        access_token = await create_access_token(data={'sub': user['username']})
        premium_status = user.get('premium', False)
        return {'access_token': access_token, 'token_type': 'bearer', 'premium': premium_status}
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=400, detail='False')


@users.get('/close-root-for-test')
async def read_item(current_user: dict = Depends(get_current_user)):
    """
    Test OAuth2 route.
    Args:
        current_user: use access token to get user from db.
    Returns: Test message.
    """
    return {'message': 'Test route', 'owner': current_user.get('username')}


@chats.post('/')
async def create_chat_route(current_user: dict = Depends(get_current_user)):
    """
    Create a chat for a specific user and return the created chat's ID.
    Args:
        current_user:
    Returns:
        dict: A message indicating successful creation along with the chat ID.
    """
    try:
        chat_id = await create_chat(current_user['_id'])
        return {'message': 'Chat created successfully!', 'chat_id': str(chat_id)}
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail='Internal Server Error')


@chats.post('/{chat_id}/{model}/send_question')
async def send_question_route(
    chat_id: str, question: MessageModel, model: str, current_user: dict = Depends(get_current_user)
):
    """
    Send a message in a specific chat with provided question and answer.
    Args:
        model:
        current_user:
        chat_id: The ID of the chat to which the message is being sent.
        question: The question or input message.
    Returns:
        dict: A message indicating successful message sending.
    """
    collection_files = await get_collection('files', 'storage')
    files_list = await collection_files.find({'chat_id': chat_id}).to_list(length=None)
    if files_list:
        content = files_list[-1].get('text')
        try:
            return {'answer': await create_message(chat_id, question.question, model, content)}
        except Exception as e:
            logging.error(e)
            raise HTTPException(status_code=500, detail='Internal Server Error')
    else:
        try:
            return {'answer': await create_message(chat_id, question.question, model)}
        except Exception as error:
            logging.error(error)
            raise HTTPException(status_code=500, detail='Internal Server Error')


@chats.get('/{chat_id}/history')
async def show_chat_history(chat_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get the chat history for a specific chat ID.
    Args:
        current_user:
        chat_id: The ID of the chat for which the history is requested.
    Returns:
        dict: A dictionary containing chat history or a message if no history found.
    """
    try:
        chat_history = await get_chat_history(chat_id)
        if not chat_history:
            return {'message': 'No chat history found for this chat_id'}
        else:
            return {'chat_history': chat_history}
    except Exception:
        raise HTTPException(status_code=500, detail='Internal Server Error')


@main.get('/', include_in_schema=False)
def get_data():
    return FileResponse('static/main.html')


@chats.get('/', include_in_schema=False)
def get_data():
    return FileResponse('static/chat.html')


@chats.delete('/{chat_id}')
async def delete_chat(chat_id: str):
    """
    Delete a specific chat and its messages by chat_id.
    Args:
        chat_id: The ID of the chat to be deleted.
    Returns:
        dict: A message indicating successful deletion.
    """
    collection_chat = await get_collection('chats')
    collection_msg = await get_collection('messages')
    try:
        await collection_chat.delete_one({'_id': ObjectId(chat_id)})
        await collection_msg.delete_many({'chat_id': chat_id})
        return {'message': f'Chat with ID: {chat_id} and its messages deleted successfully'}
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail='Internal Server Error')


@chats.get('/user_chats')
async def get_user_chats(current_user: dict = Depends(get_current_user)):
    """
    Get all chat IDs for the current user.
    Args:
        current_user: The current authenticated user.
    Returns:
        dict: A dictionary containing the list of chat IDs for the user.
    """
    try:
        collection_chat = await get_collection('chats')
        user_chats = await collection_chat.find({'user_id': current_user['_id']}).to_list(length=None)
        chat_ids = [str(chat['_id']) for chat in user_chats]
        return {'chat_ids': chat_ids}
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail='Internal Server Error')


@files.post('/{chat_id}/upload/')
async def upload_file(chat_id, file: UploadFile = File(...)):
    """
    Uploads a file and processes it based on its content type.

    This endpoint accepts a file upload and processes the file based on its MIME type. It supports processing for
    PDF, CSV, DOCX, and plain text files. The processed text is then stored in a MongoDB collection, and the function
    returns the ID of the created database entry along with the file name.

    Args:
        chat_id:
        file (UploadFile): The file to be uploaded. Accepted types are PDF, CSV, DOCX, and plain text.

    Returns: JSONResponse: A response object containing the ID of the created database entry and the file's name. The
    response status code is set to 200 for a successful upload.

    Raises: HTTPException: If the file type is unsupported or if an error occurs during file processing or database
    insertion, an HTTPException with status code 400 (for unsupported file type) or 500 (for other errors) is raised.

    Note: The function includes a size check for CSV, DOCX, and plain text files. If the content length exceeds 4000
    characters, a response indicating a size warning is returned.

    Example: To use this endpoint, send a POST request with a file to '/upload/'. The response will contain the
    file's ID in the database and its name.
    """
    try:
        file_content = await file.read()

        if file.content_type == 'application/pdf':
            text = extract_text_from_pdf(BytesIO(file_content))

        elif file.content_type == 'text/csv':
            if len(file_content.decode('utf-8')) > 4000:
                return size_warning_response()
            text = str(extract_data_from_csv(StringIO(file_content.decode('utf-8'))))

        elif file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text = extract_text_from_docx(BytesIO(file_content))
            if len(text) > 4000:
                return size_warning_response()

        elif file.content_type == 'text/plain':
            text = file_content.decode('utf-8')
            if len(text) > 4000:
                return size_warning_response()

        else:
            raise HTTPException(status_code=400, detail='Unsupported file type')

        mongo_client = await get_mongodb()
        collection = mongo_client['files']
        await collection.insert_one({'text': text, 'name': file.filename, 'chat_id': chat_id})

        return JSONResponse(content=text, status_code=200)

    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail=f'Error processing file: {str(e)}')


@users.post('/pay')
async def pay(current_user: dict = Depends(get_current_user)):
    """
    Args:
        current_user:
    Returns:
        username of current user
    """
    return await get_payment(current_user.get('username'))


@payment.get('/execute')
async def execute_payment(request: Request):
    """
    Executes a payment transaction based on the provided payment ID and payer ID.
    Args:
        request (Request): The request object, used to extract query parameters.

    Returns:
        dict: A status message indicating the result of the payment execution. This includes successful
              completion or failure details.

    Raises:
        HTTPException: If the payment ID or payer ID is missing, or if the payment execution fails.

    Note:
        The actual payment execution is handled by `execute_paypal_payment()`, which should manage the
        interaction with the PayPal API or similar payment service. The function checks for the presence
        of 'paymentId' and 'PayerID' in the query parameters and uses them along with the current user's
        information to execute the payment.
    """
    payment_id = request.query_params.get('paymentId')
    payer_id = request.query_params.get('PayerID')

    session = await get_collection('users')
    current_user = await session.find_one({'token': request.query_params.get('token')})

    if payment_id and payer_id:
        success = await execute_paypal_payment(payment_id, payer_id, current_user.get('username'))

        if success:
            return FileResponse('static/pay-result.html')
        else:
            return {'status': 'Payment failed. Try again.'}
    else:
        return {'status': 'Missing paymentId or PayerID. Try again or send a feedback.'}
