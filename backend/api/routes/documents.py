from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/upload/")
async def upload_document(file: UploadFile, project_id: int = Form(...)):
    content = await file.read()
    text = content.decode("utf-8")
    return {"message": "Uploaded", "text": text}