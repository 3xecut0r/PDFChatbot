from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    username_mongo: str = Field(..., env="USERNAME_MONGO") 
    password_mongo: str = Field(..., env="PASSWORD_MONGO") 

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8' 


settings = Settings()
