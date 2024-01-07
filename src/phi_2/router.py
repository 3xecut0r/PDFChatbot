from fastapi import APIRouter, UploadFile, File
from typing import List, Optional
import transformers
from langchain import PromptTemplate, LLMChain
from langchain.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.routers.pdf import upload_pdf
from .training.generate import InstructionTextGenerationPipeline, load_model_tokenizer_for_generate
from .schemas import TextGenerationRequest

router = APIRouter()
default_model = "databricks/dolly-v2-3b"
embeddings = HuggingFaceEmbeddings()

model, tokenizer = load_model_tokenizer_for_generate(default_model)


def generate_text(input_text: str) -> str:
    pipeline = transformers.pipeline(
        model="databricks/dolly-v2-3b",
        trust_remote_code=True
    )
    res = pipeline(input_text)
    print(f"Result from pipeline: {res}")
    return res[0][0]["generated_text"]

prompt = PromptTemplate(
    input_variables=["instruction"],
    template="{instruction}"
)
prompt_with_context = PromptTemplate(
    input_variables=["instruction", "context"],
    template="{instruction}\n\nInput:\n{context}"
)

hf_pipeline = HuggingFacePipeline(pipeline=InstructionTextGenerationPipeline(model=model, tokenizer=tokenizer, return_full_text=True, task="text-generation"))
llm_chain = LLMChain(llm=hf_pipeline, prompt=prompt)
llm_context_chain = LLMChain(llm=hf_pipeline, prompt=prompt_with_context)


@router.post("/generate-text/")
async def gen_text(instruction: str, context: str = None,  file: UploadFile = File(None)):
    additional_context = ""
    if file:
        upload_result = await upload_pdf(file)
        print("SUCCESS")
        print("*"*100)
        if upload_result:
            additional_context += " " + upload_result["text"]

    if context:
        print("with context")
        context_to_use = context + " " + additional_context  
        generated_text = llm_context_chain.run(instruction=instruction, context=context_to_use)
    else:
        print("without context")
        context_to_use = additional_context
        generated_text = llm_chain.run(instruction=instruction, context=context_to_use)

    # embedding_result = embeddings.embed_query(generated_text)
    # return {"generated_text": generated_text, "embedding": embedding_result}
    return generated_text


