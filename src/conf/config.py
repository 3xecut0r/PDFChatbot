from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    username_mongo: str = Field(..., env="USERNAME_MONGO") 
    password_mongo: str = Field(..., env="PASSWORD_MONGO")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    paypal_client: str = Field(..., env="PAYPAL_CLIENT")
    paypal_secret: str = Field(..., env="PAYPAL_SECRET")
    class Config:
        env_file = '.env.sample'
        env_file_encoding = 'utf-8' 


settings = Settings()
