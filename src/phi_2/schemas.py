from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    text: str
    max_length: int = 200
    