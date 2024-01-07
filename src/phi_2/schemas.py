from pydantic import BaseModel


class TextGenerationRequest(BaseModel):
    instruction: str
    context: str