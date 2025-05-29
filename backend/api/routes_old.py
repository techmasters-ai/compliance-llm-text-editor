# backend/api/routes.py
from fastapi import APIRouter, Depends
from db import session, models
from core import parser, workflow
from sqlalchemy.orm import Session
from api.schemas import UploadRequest, RuleCheckRequest, EditAcceptRequest

router = APIRouter()

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
def upload_doc(data: UploadRequest, db: Session = Depends(get_db)):
    doc = models.Document(name=data.name, content=data.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    for para in parser.break_into_paragraphs(data.content):
        db.add(models.Paragraph(document_id=doc.id, content=para))
    db.commit()
    return {"document_id": doc.id}

@router.get("/document_paragraphs")
def get_paragraphs(doc_id: int, db: Session = Depends(get_db)):
    return db.query(models.Paragraph).filter(models.Paragraph.document_id == doc_id).all()

@router.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    return db.query(models.ComplianceRule).all()

@router.post("/check_violation")
def check_rule(data: RuleCheckRequest, db: Session = Depends(get_db)):
    rule = db.query(models.ComplianceRule).filter(models.ComplianceRule.id == data.rule_id).first()
    para = db.query(models.Paragraph).filter(models.Paragraph.id == data.paragraph_id).first()
    result = workflow.evaluate_paragraph(para.content, rule.description)
    v = models.Violation(paragraph_id=para.id, rule_id=rule.id, highlighted_text=result)
    db.add(v)
    db.commit()
    return {"violation_id": v.id, "highlighted_text": result}

@router.post("/suggest_fix")
def fix_violation(violation_id: int, db: Session = Depends(get_db)):
    v = db.query(models.Violation).filter(models.Violation.id == violation_id).first()
    suggestion = workflow.generate_fix(v.highlighted_text, v.paragraph.violations[0].paragraph.content)
    v.suggested_fix = suggestion
    db.commit()
    return {"suggested_fix": suggestion}

@router.post("/accept_edit")
def accept_edit(data: EditAcceptRequest, db: Session = Depends(get_db)):
    v = db.query(models.Violation).filter(models.Violation.id == data.violation_id).first()
    para = db.query(models.Paragraph).filter(models.Paragraph.id == v.paragraph_id).first()
    para.content = data.new_text
    v.accepted = data.accepted
    db.commit()
    return {"status": "updated"}
