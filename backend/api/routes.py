from fastapi import APIRouter, Depends, HTTPException
from db import session, models
from core import parser, workflow
from sqlalchemy.orm import Session
from sqlalchemy import asc
from api.schemas import (
    UploadRequest, RuleCheckRequest, EditAcceptRequest,
    GenerateRulesRequest, GenerateRulesResponse, ParagraphWithNeighborsResponse, 
    RuleUpdateRequest, LLMQueryRequest, LLMQueryResponse, FixSuggestionsRequest
)

router = APIRouter()

def get_db():
    db = session.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# NEW: Upload document for rule generation (no paragraph splitting)
@router.post("/upload_for_rules")
def upload_for_rules(data: UploadRequest, db: Session = Depends(get_db)):
    doc = models.Document(name=data.name, content=data.content)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"document_id": doc.id}

# Existing but renamed for clarity
@router.post("/upload_for_checking")
def upload_for_checking(data: UploadRequest, db: Session = Depends(get_db)):
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

@router.post("/generate_rules", response_model=GenerateRulesResponse)
def generate_rules(data: GenerateRulesRequest, db: Session = Depends(get_db)):
    rules = workflow.generate_compliance_rules(data.text)
    created_ids = []
    for i, rule in enumerate(rules):
        rule_obj = models.ComplianceRule(name=f"Rule {i+1}", description=rule)
        db.add(rule_obj)
        db.commit()
        db.refresh(rule_obj)
        created_ids.append(rule_obj.id)
    return {"rules": rules}

@router.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    return db.query(models.ComplianceRule).all()

@router.get("/rules/{rule_id}")
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.ComplianceRule).filter(models.ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

# Update an existing compliance rule
@router.put("/rules/{rule_id}")
def update_rule(rule_id: int, data: RuleUpdateRequest, db: Session = Depends(get_db)):
    rule = db.query(models.ComplianceRule).filter(models.ComplianceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.name = data.name
    rule.description = data.description
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name, "description": rule.description}

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
def fix_violations(data: FixSuggestionsRequest, db: Session = Depends(get_db)):
    if not data.violation_ids:
        raise HTTPException(status_code=400, detail="No violation IDs provided")

    violations = db.query(models.Violation).filter(models.Violation.id.in_(data.violation_ids)).all()
    if not violations:
        raise HTTPException(status_code=404, detail="No matching violations found")

    # Assume all violations are for the same paragraph
    paragraph = violations[0].paragraph
    rule_texts = [v.highlighted_text for v in violations]

    combined_prompt_context = "\n\n".join(rule_texts)
    suggestion = workflow.get_fix_suggestion(paragraph.content, combined_prompt_context)

    # Optional: update each violation with same suggestion
    for v in violations:
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

@router.get("/paragraph_with_neighbors/{paragraph_id}", response_model=ParagraphWithNeighborsResponse)
def get_paragraph_with_neighbors(paragraph_id: int, db: Session = Depends(get_db)):
    target = db.query(models.Paragraph).filter(models.Paragraph.id == paragraph_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Paragraph not found")

    all_paragraphs = db.query(models.Paragraph).filter(
        models.Paragraph.document_id == target.document_id
    ).order_by(asc(models.Paragraph.id)).all()

    index = next((i for i, p in enumerate(all_paragraphs) if p.id == paragraph_id), None)

    return {
        "previous": all_paragraphs[index - 1] if index > 0 else None,
        "current": all_paragraphs[index],
        "next": all_paragraphs[index + 1] if index < len(all_paragraphs) - 1 else None
    }

@router.post("/llm_query", response_model=LLMQueryResponse)
def general_llm_query(data: LLMQueryRequest):
    return workflow.get_llm_response(data.prompt)