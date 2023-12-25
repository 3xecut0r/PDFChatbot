from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from io import BytesIO
import pdfplumber
from src.utils.get_mongo import get_mongodb

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_content = BytesIO(await file.read())
        pdf_content.seek(0)

        text = extract_text_from_pdf(pdf_content)

        mongo_client = await get_mongodb()

        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})

        response_dict = {"text": text, "name": file.filename, "id": str(result.inserted_id)}
        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


def extract_text_from_pdf(pdf_content):
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()
    return text
