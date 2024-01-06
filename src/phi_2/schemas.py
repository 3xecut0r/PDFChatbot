from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    context: str
