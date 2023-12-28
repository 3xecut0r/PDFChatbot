from fastapi import File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse

from io import BytesIO, StringIO
from docx import Document
import pdfplumber
import csv

from src.utils.get_mongo import get_mongodb

# router = APIRouter(prefix="/pdf", tags=["pdf"])
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload-pdf/")

async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_content = BytesIO(await file.read())
        pdf_content.seek(0)

        text = extract_text_from_pdf(pdf_content)

        mongo_client = await get_mongodb()

        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})


        response_dict = {
            "text": text,
            "name": file.filename,
            "id": str(result.inserted_id),
        }
  
        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


def extract_text_from_pdf(pdf_content):
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()
    return text



@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):
    try:
        if file.content_type != "text/csv":
            raise HTTPException(status_code=400, detail="File is not a CSV")

        file_content = await file.read()

        # Треба буде зробити реалізацію на стороні юзера
        file_content_decoded = file_content.decode("utf-8")
        if len(file_content_decoded) > 4000:
            return JSONResponse(
                content={
                    "warning": "File size exceeds 4000 symbols. Please reduce the file size or abort the operation.",
                    "action_required": True,
                },
                status_code=200,
            )

        csv_content = StringIO(file_content.decode("utf-8"))
        csv_content.seek(0)

        data = extract_data_from_csv(csv_content)

        mongo_client = await get_mongodb()
        collection = mongo_client["files"]
        result = await collection.insert_one({"data": data, "name": file.filename})

        response_dict = {
            "data": data,
            "name": file.filename,
            "id": str(result.inserted_id),
        }
        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")


def extract_data_from_csv(csv_content):
    reader = csv.DictReader(csv_content)
    data = [row for row in reader]
    return data


@router.post("/upload-docx/")
async def upload_docx(file: UploadFile = File(...)):
    try:
        if (
            file.content_type
            != "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            raise HTTPException(status_code=400, detail="File is not a DOCX")

        doc = Document(file.file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        if len(text) > 4000:
            return JSONResponse(
                content={
                    "warning": "File size exceeds 4000 symbols. Please reduce the file size or abort the operation.",
                    "action_required": True,
                },
                status_code=200,
            )

        mongo_client = await get_mongodb()
        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})

        response_dict = {
            "text": text,
            "name": file.filename,
            "id": str(result.inserted_id),
        }

        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing DOCX: {str(e)}")


@router.post("/upload-txt/")
async def upload_txt(file: UploadFile = File(...)):
    try:
        if file.content_type != "text/plain":
            raise HTTPException(status_code=400, detail="File is not a TXT")

        text = (await file.read()).decode("utf-8")

        if len(text) > 4000:
            return JSONResponse(
                content={
                    "warning": "File size exceeds 4000 symbols. Please reduce the file size or abort the operation.",
                    "action_required": True,
                },
                status_code=200,
            )

        mongo_client = await get_mongodb()
        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})

        response_dict = {
            "text": text,
            "name": file.filename,
            "id": str(result.inserted_id),
        }

        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing TXT: {str(e)}")

