from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from io import BytesIO
import pdfplumber

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Read the content of the PDF file
        pdf_content = BytesIO(await file.read())
        pdf_content.seek(0)  # Reset the read pointer to the beginning

        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_content)

        # Return a dictionary with text and file name
        response_dict = {"text": text, "name": file.filename}
        return JSONResponse(content=response_dict, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


def extract_text_from_pdf(pdf_content):
    # Extract text from the PDF
    text = ""
    with pdfplumber.open(pdf_content) as pdf:
        for page_num in range(len(pdf.pages)):
            text += pdf.pages[page_num].extract_text()

    return text
