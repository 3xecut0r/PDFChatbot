from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_version: str = "1.0.1"
    username_mongo: str = Field(..., env='USERNAME_MONGO')
    password_mongo: str = Field(..., env='PASSWORD_MONGO')
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    paypal_client: str = Field(..., env='PAYPAL_CLIENT')
    paypal_secret: str = Field(..., env='PAYPAL_SECRET')
    hf_api_key: str = Field(..., env='HF_API_KEY')

    class Config:
        env_file = '.env.sample'
        env_file_encoding = 'utf-8'

    @property
    def mongo_url(self) -> str:
        return f'mongodb+srv://{self.username_mongo}:{self.password_mongo}@pdfchatbot.zkaopxh.mongodb.net/?retryWrites=true&w=majority'


settings = Settings()
