from fastapi import FastAPI
from backend.api.routes import documents

app = FastAPI()
app.include_router(documents.router, prefix="/documents")