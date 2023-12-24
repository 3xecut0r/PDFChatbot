from fastapi import APIRouter, Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas import UserModel
from src.templates.auth import Hash, create_access_token, get_current_user
from src.templates.operations import create_user, get_db

users = APIRouter(prefix='/users', tags=['users'])

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
