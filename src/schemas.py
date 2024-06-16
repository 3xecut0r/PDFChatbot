from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str = 'OK'


class UserModel(BaseModel):
    username: str
    password: str


class ChatModel(BaseModel):
    user_id: str


class MessageModel(BaseModel):
    question: str
    model: str

