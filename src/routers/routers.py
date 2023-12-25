from fastapi import APIRouter, Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas import UserModel
from src.templates.auth import Hash, create_access_token, get_current_user
from src.templates.operations import create_user, get_db
from src.templates.operations import create_chat, send_message, get_chat_history

users = APIRouter(prefix='/users', tags=['users'])
chats = APIRouter(prefix='/chat', tags=['chats'])

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
            user = await collection.find_one({'username': body.username})
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
        if not hash_handler.verify_password(body.password, user['password']):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        access_token = await create_access_token(data={"sub": user['username']})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail='False')


@users.get("/close-root-for-test")
async def read_item(current_user: dict = Depends(get_current_user)):
    """
    Test OAuth2 route.
    Args:
        current_user: use access token to get user from db.
    Returns: Test message.
    """
    return {"message": "Test route", "owner": current_user.get("username")}


@chats.post("/create/{user_id}")
async def create_chat_route(user_id: str):
    """
    Create a chat for a specific user and return the created chat's ID.
    Args:
        user_id: The ID of the user for whom the chat is being created.
    Returns:
        dict: A message indicating successful creation along with the chat ID.
    """
    try:
        chat_id = await create_chat(user_id)
        return {"message": "Chat created successfully!", "chat_id": str(chat_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@chats.post("/{chat_id}/send_message")
async def send_message_route(chat_id: str, question: str, answer: str):
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
        await send_message(chat_id, question, answer)
        return {"message": "Message sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@chats.get("/history/{chat_id}")
async def show_chat_history(chat_id: str):
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