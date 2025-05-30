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

class GenerateRulesRequest(BaseModel):
    text: str

class GenerateRulesResponse(BaseModel):
    rules: list[str]

class ParagraphOut(BaseModel):
    id: int
    document_id: int
    content: str

    class Config:
        orm_mode = True

class ParagraphWithNeighborsResponse(BaseModel):
    previous: ParagraphOut | None
    current: ParagraphOut
    next: ParagraphOut | None

class RuleUpdateRequest(BaseModel):
    name: str
    description: str

class LLMQueryRequest(BaseModel):
    prompt: str

class LLMQueryResponse(BaseModel):
    response: str
