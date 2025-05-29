# backend/main.py
from fastapi import FastAPI
from api.routes import router
from db.models import Base
from db.session import engine

app = FastAPI()
app.include_router(router)

Base.metadata.create_all(bind=engine)
