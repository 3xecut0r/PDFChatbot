from fastapi import APIRouter, Depends, UploadFile, File

from src.templates.auth import get_current_user
from .basemodel import BASEMODEL, save_message


base = APIRouter(prefix='/basemodel', tags=['base'])


@base.post('/question')
async def simple_answer(question, file: UploadFile = File(None), current_user: dict = Depends(get_current_user)):
    if file:
        content = await file.read()
        text = BASEMODEL.upload_pdf(file.filename, content)  
        answer = await BASEMODEL.answer(f"Question:{question} \n\n {text}")
    else:
        answer = await BASEMODEL.answer(question)
    return answer
