from bson import ObjectId
from jinja2 import Template

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse as redirect

from src.schemas import UserModel, MessageModel
from src.templates.auth import Hash, create_access_token, get_current_user
from src.templates.operations import (
    create_user,
    get_db,
    get_payment,
    execute_paypal_payment,
    )
from src.templates.operations import (
    create_chat, 
    create_message, 
    get_chat_history, 
    get_chat_data, 
    get_msg_data 
    )
from src.templates.operations import (
    size_warning_response,
    extract_text_from_pdf,
    extract_data_from_csv,
    extract_text_from_docx,
)


from starlette.responses import FileResponse

from fastapi import File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse

from io import BytesIO, StringIO
from docx import Document
from fastapi.responses import HTMLResponse

from src.utils.get_mongo import get_mongodb

main = APIRouter(prefix='/main', tags=['main'])
users = APIRouter(prefix='/users', tags=['users'])
chats = APIRouter(prefix='/chats', tags=['chats'])
router = APIRouter(prefix="/files", tags=["files"])
payment = APIRouter(prefix='/payment', tags=['payment'])


hash_handler = Hash()


@users.post("/signup", status_code=status.HTTP_201_CREATED)
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
    return "Created!"


@users.post("/signin")
async def login(body: OAuth2PasswordRequestForm = Depends()):
    """
    Sign in function.
    Args:
        body: OAuth2PasswordRequestForm.
    Returns: user access token.
    """
    try:
        collection = get_db()
        try:
            user = await collection.find_one({"username": body.username})
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
            )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
            )
        if not hash_handler.verify_password(body.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )

        access_token = await create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="False")


@users.get("/close-root-for-test")
async def read_item(current_user: dict = Depends(get_current_user)):
    """
    Test OAuth2 route.
    Args:
        current_user: use access token to get user from db.
    Returns: Test message.
    """
    return {"message": "Test route", "owner": current_user.get("username")}


@chats.post("/")
async def create_chat_route(current_user: dict = Depends(get_current_user)):
    """
    Create a chat for a specific user and return the created chat's ID.
    Args:
        user_id: The ID of the user for whom the chat is being created.
    Returns:
        dict: A message indicating successful creation along with the chat ID.
    """
    try:
        chat_id = await create_chat(current_user["_id"])
        return {"message": "Chat created successfully!", "chat_id": str(chat_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@chats.post("/{chat_id}/send_question")
async def send_question_route(
    chat_id: str, question: MessageModel, current_user: dict = Depends(get_current_user)
):
    """
    Send a message in a specific chat with provided question and answer.
    Args:
        chat_id: The ID of the chat to which the message is being sent.
        question: The question or input message.
        answer: The provided answer for the given question.
    Returns:
        dict: A message indicating successful message sending.
    """
    try:
        answer = await create_message(chat_id, question.question)
        return {"answer": answer}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@chats.get("/{chat_id}/history")
async def show_chat_history(
    chat_id: str, current_user: dict = Depends(get_current_user)
):
    """
    Get the chat history for a specific chat ID.
    Args:
        chat_id: The ID of the chat for which the history is requested.
    Returns:
        dict: A dictionary containing chat history or a message if no history found.
    """
    try:
        chat_history = await get_chat_history(chat_id)
        if not chat_history:
            return {"message": "No chat history found for this chat_id"}
        else:
            return {"chat_history": chat_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@main.get("/", include_in_schema=False)
def get_data():
    return FileResponse("static/main.html")


@chats.get("/", include_in_schema=False)
def get_data():
    return FileResponse("static/chat.html")


@chats.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    """
    Delete a specific chat and its messages by chat_id.
    Args:
        chat_id: The ID of the chat to be deleted.
    Returns:
        dict: A message indicating successful deletion.
    """
    collection_chat = get_chat_data()
    collection_msg = get_msg_data()
    try:
        await collection_chat.delete_one({"_id": ObjectId(chat_id)})
        await collection_msg.delete_many({"chat_id": chat_id})
        return {"message": f"Chat with ID: {chat_id} and its messages deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@chats.get("/user_chats")
async def get_user_chats(current_user: dict = Depends(get_current_user)):
    """
    Get all chat IDs for the current user.
    Args:
        current_user: The current authenticated user.
    Returns:
        dict: A dictionary containing the list of chat IDs for the user.
    """
    try:
        collection_chat = get_chat_data()  # Отримайте колекцію чатів з бази даних
        user_chats = await collection_chat.find({"user_id": current_user['_id']}).to_list(length=None)
        chat_ids = [str(chat['_id']) for chat in user_chats]
        return {"chat_ids": chat_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file and processes it based on its content type.

    This endpoint accepts a file upload and processes the file based on its MIME type. It supports processing for PDF, CSV, DOCX, and plain text files. The processed text is then stored in a MongoDB collection, and the function returns the ID of the created database entry along with the file name.

    Args:
        file (UploadFile): The file to be uploaded. Accepted types are PDF, CSV, DOCX, and plain text.

    Returns:
        JSONResponse: A response object containing the ID of the created database entry and the file's name. The response status code is set to 200 for a successful upload.

    Raises:
        HTTPException: If the file type is unsupported or if an error occurs during file processing or database insertion, an HTTPException with status code 400 (for unsupported file type) or 500 (for other errors) is raised.

    Note:
        The function includes a size check for CSV, DOCX, and plain text files. If the content length exceeds 4000 characters, a response indicating a size warning is returned.

    Example:
        To use this endpoint, send a POST request with a file to '/upload/'. The response will contain the file's ID in the database and its name.
    """
    try:
        file_content = await file.read()

        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(BytesIO(file_content))

        elif file.content_type == "text/csv":
            if len(file_content.decode("utf-8")) > 4000:
                return size_warning_response()
            data = extract_data_from_csv(StringIO(file_content.decode("utf-8")))
            text = str(data)

        elif (
            file.content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            text = extract_text_from_docx(BytesIO(file_content))
            if len(text) > 4000:
                return size_warning_response()

        elif file.content_type == "text/plain":
            text = file_content.decode("utf-8")
            if len(text) > 4000:
                return size_warning_response()

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        mongo_client = await get_mongodb()
        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})

        return JSONResponse(
            content={
                "id": str(result.inserted_id),  # Return only the ID
                "name": file.filename,
            },
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@users.post("/pay")
async def pay(current_user: dict = Depends(get_current_user)):
    """
    Initiates a payment process for the current user.

    Args:
        current_user (dict): The current authenticated user obtained from the dependency `get_current_user`.

    Returns:
        dict: The result of the payment initiation process. The structure of this response depends on
              the implementation of `get_payment()`.

    Raises:
        HTTPException: If any errors occur during the payment initiation process.

    Note:
        This function assumes that `get_payment()` handles the actual logic of initiating a payment and
        may interact with external payment services. The current user's details are used to personalize
        or authorize the payment process.
    """
    result = await get_payment()
    return result


@payment.get("/execute", include_in_schema=False)
async def execute_payment(
    request: Request, current_user: dict = Depends(get_current_user)
):
    """
    Executes a payment transaction based on the provided payment ID and payer ID.
    Args:
        request (Request): The request object, used to extract query parameters.
        current_user (dict): The current authenticated user, used to validate and associate the payment.

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
    payment_id = request.query_params.get("paymentId")
    payer_id = request.query_params.get("PayerID")

    if payment_id and payer_id:
        success = await execute_paypal_payment(
            payment_id, payer_id, current_user.get("username")
        )

        if success:
            status_text = "Payment successful, user upgraded to premium"
        else:
            status_text = "Payment failed"
    else:
        status_text = "Missing paymentId or PayerID"

    with open("static/pay-result.html", "r") as file:
        template = Template(file.read())

    html_content = template.render(payment_status=status_text)
    return HTMLResponse(content=html_content, status_code=200)
