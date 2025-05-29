# backend/api/schemas.py
from pydantic import BaseModel

class UploadRequest(BaseModel):
    name: str
    content: str

class RuleCheckRequest(BaseModel):
    rule_id: int
    paragraph_id: int

class EditAcceptRequest(BaseModel):
    violation_id: int
    new_text: str
    accepted: bool
