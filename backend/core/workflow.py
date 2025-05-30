# backend/core/workflow.py
import logging
from core.llm import check_violation, suggest_fix, generate_compliance_rules, general_llm_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_paragraph(paragraph, rule_description):
    result = check_violation(paragraph, rule_description)
    return result

def get_fix_suggestion(paragraph, rule_description):
    return suggest_fix(paragraph, rule_description)

def get_compliance_rules(document):
    return  generate_compliance_rules(document)

def get_llm_response(query):
    return general_llm_query(query)


