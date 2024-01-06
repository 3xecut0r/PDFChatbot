from fastapi import APIRouter
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import transformers
import torch
from .schemas import TextGenerationRequest

router = APIRouter()


@router.post("/generate-text/")
async def generate_text(request: TextGenerationRequest):
    inputs = tokenizer(request.text, return_tensors="pt", return_attention_mask=False)
    try:
        outputs = model.generate(**inputs, max_length=request.max_length)
        generated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return {"generated_text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def gen_text(model: TextGenerationRequest) -> str:
    generate_text = transformers.pipeline(
        model="databricks/dolly-v2-3b",
        trust_remote_code=True
    )

    res = generate_text(f"{model.context}")
    return res[0]["generated_text"]

