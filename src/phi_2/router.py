from fastapi import APIRouter, HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from .schemas import TextGenerationRequest


model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype=torch.float32, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)

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
