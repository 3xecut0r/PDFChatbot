from fastapi import File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse

from io import BytesIO, StringIO
from docx import Document
import pdfplumber
import csv

from src.utils.get_mongo import get_mongodb

# router = APIRouter(prefix="/pdf", tags=["pdf"])
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()

        if file.content_type == "application/pdf":
            text = extract_text_from_pdf(BytesIO(file_content))

        elif file.content_type == "text/csv":
            if len(file_content.decode("utf-8")) > 4000:
                return size_warning_response()
            data = extract_data_from_csv(StringIO(file_content.decode("utf-8")))
            text = str(data)

        elif (
            file.content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            text = extract_text_from_docx(BytesIO(file_content))
            if len(text) > 4000:
                return size_warning_response()

        elif file.content_type == "text/plain":
            text = file_content.decode("utf-8")
            if len(text) > 4000:
                return size_warning_response()

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        mongo_client = await get_mongodb()
        collection = mongo_client["files"]
        result = await collection.insert_one({"text": text, "name": file.filename})

        # return JSONResponse(
        #     content={
        #         "text": text,
        #         "name": file.filename,
        #         "id": str(result.inserted_id),
        #     },
        #     status_code=200,
        # )

        # Return the ID of the inserted document
        return JSONResponse(
            content={
                "id": str(result.inserted_id),  # Return only the ID
                "name": file.filename,
            },
            status_code=200,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


def size_warning_response():
    return JSONResponse(
        content={
            "warning": "File size exceeds 4000 symbols. Please reduce the file size or abort the operation.",
            "action_required": True,
        },
        status_code=200,
    )


def extract_text_from_pdf(pdf_content):
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()
    return text


def extract_data_from_csv(csv_content):
    reader = csv.DictReader(csv_content)
    data = [row for row in reader]
    return data


def extract_text_from_docx(doc_content):
    doc = Document(doc_content)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])
