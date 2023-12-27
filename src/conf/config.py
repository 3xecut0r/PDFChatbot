from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    username_mongo: str = Field(..., env="USERNAME_MONGO") 
    password_mongo: str = Field(..., env="PASSWORD_MONGO")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8' 


settings = Settings()
