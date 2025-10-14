from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Code Review Assistant Backend",
    description="Handles file uploads and code analysis",
    version="0.1.0"
)

app.include_router(router)
