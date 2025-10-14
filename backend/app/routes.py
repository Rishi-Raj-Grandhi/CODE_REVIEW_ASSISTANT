from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.services import process_uploaded_input

# Initialize router
router = APIRouter()

@router.post("/upload/file/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    file_data = {"filename": file.filename, "content": content}
    result = process_uploaded_input("file", file_data)
    return JSONResponse(content=result)


@router.post("/upload/files/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append({"filename": file.filename, "content": content})
    result = process_uploaded_input("files", file_data)
    return JSONResponse(content=result)


@router.post("/upload/folder/")
async def upload_folder(zip_file: UploadFile = File(...)):
    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")
    zip_bytes = await zip_file.read()
    result = process_uploaded_input("zip", zip_bytes)
    return JSONResponse(content=result)
