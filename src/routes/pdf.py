from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
from src.utils.get_mongo import get_mongodb
import PyPDF2

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), mongodb=Depends(get_mongodb)):
    if file.content_type != "application/pdf":
        return JSONResponse(content={"error": "Только PDF файлы"}, status_code=400)

    try:
        pdf_reader = PyPDF2.PdfFileReader(file.file)
        text = ""

        # Извлечение текста
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()

        # Сохранение текста
        pdf_data = {"filename": file.filename, "text": text}
        mongodb_text = upload_pdf_text(mongodb, pdf_data)

        return {"filename": file.filename, "text": text, "mongodb_id": str(mongodb_text.inserted_id)}
    except Exception as e:
        return JSONResponse(content={"error": f"Ошибка обработки PDF: {str(e)}"}, status_code=500)


# Пока так, но тут вопрос как мы будем его сохранять
def upload_pdf_text(mongodb: Collection, pdf_data: dict):
    return mongodb.insert_one(pdf_data)
