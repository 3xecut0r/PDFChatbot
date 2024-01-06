from fastapi import APIRouter
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import transformers
import torch
from .schemas import TextGenerationRequest

router = APIRouter()


@router.post("/generate-text/")
def gen_text(model: TextGenerationRequest) -> str:
    generate_text = transformers.pipeline(
        model="databricks/dolly-v2-3b",
        trust_remote_code=True
    )

    res = generate_text(f"{model.context}")
    return res[0]["generated_text"]
