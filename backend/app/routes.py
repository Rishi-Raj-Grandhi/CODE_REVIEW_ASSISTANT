from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from app.services import process_uploaded_input
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services import register_user, login_user ,save_to_db

# Initialize router
router = APIRouter()

# ---- ROUTES ----

@router.post("/upload/file/")
async def upload_file(
    user_id: str = Form(...), 
    file: UploadFile = File(...)
):
    content = await file.read()
    file_data = {"filename": file.filename, "content": content}
    result = process_uploaded_input("file", file_data)

    # store in DB
    save_to_db(user_id, "file", result)

    return JSONResponse(content=result)


@router.post("/upload/files/")
async def upload_files(
    user_id: str = Form(...), 
    files: List[UploadFile] = File(...)
):
    file_data = []
    for file in files:
        content = await file.read()
        file_data.append({"filename": file.filename, "content": content})

    result = process_uploaded_input("files", file_data)

    # store in DB
    save_to_db(user_id, "files", result)

    return JSONResponse(content=result)


@router.post("/upload/folder/")
async def upload_folder(
    user_id: str = Form(...), 
    zip_file: UploadFile = File(...)
):
    if not zip_file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")

    zip_bytes = await zip_file.read()
    result = process_uploaded_input("zip", zip_bytes)

    # store in DB
    save_to_db(user_id, "zip", result)

    return JSONResponse(content=result)


@router.post("/auth/register/")
async def register(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Registers a new user with username and password.
    User ID is auto-generated on backend.
    """
    result = register_user(username, password)
    return JSONResponse(content=result)


@router.post("/auth/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Logs in a user using username and password.
    """
    result = login_user(username, password)
    return JSONResponse(content=result)