from fastapi import APIRouter, Depends,  HTTPException, status, Request
from .basemodel import BASEMODEL


base = APIRouter(prefix='/basemodel', tags=['base'])


@base.post('/question')
async def simple_answer(question):
    answer = await BASEMODEL.answer(question)
    return answer
