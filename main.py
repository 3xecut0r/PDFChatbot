from fastapi import FastAPI
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from huggingface_hub import login

from src.routers.routers import users


model_name = "tiiuae/falcon-180B"
token = "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"
login()
tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
model = AutoModelForCausalLM.from_pretrained(model_name, token=token, torch_dtype=torch.float)

text_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)


app = FastAPI()

@app.post("/generate-text/")
def generate_text(input_text: str):
    try:
        result = text_pipeline(input_text, max_length=200, num_return_sequences=1)
        return {"generated_text": result[0]['generated_text']}
    except Exception as e:
        return {"error": str(e)}


origins = [
    "http://localhost:8000"
    ]

app.include_router(users)
