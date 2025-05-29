# backend/core/workflow.py
from core.llm import check_violation, suggest_fix

def evaluate_paragraph(paragraph, rule_description):
    result = check_violation(paragraph, rule_description)
    return result

def generate_fix(highlighted, rule_description):
    return suggest_fix(highlighted, rule_description)
