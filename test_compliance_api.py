import requests
import time

BASE_URL = "http://localhost:8000"

# Sample documents
DOCUMENT_FOR_RULES = """All user data must be encrypted in transit.
Never share passwords via email.
Multi-factor authentication is required for all users.
"""

DOCUMENT_TO_CHECK = """This is a sample paragraph that may or may not be compliant.
All user data must be encrypted during transmission.
Always share passwords via email."""

# ---------- 1. Upload Rule Source Document ----------
def test_upload_for_rules():
    response = requests.post(f"{BASE_URL}/upload_for_rules", json={
        "name": "Rule Source Document",
        "content": DOCUMENT_FOR_RULES
    })
    response.raise_for_status()
    doc_id = response.json()["document_id"]
    print(f"✅ Uploaded Rule Source Document. ID: {doc_id}")
    print('')
    return doc_id

# ---------- 2. Upload Document to Check ----------
def test_upload_for_checking():
    response = requests.post(f"{BASE_URL}/upload_for_checking", json={
        "name": "Document to Check",
        "content": DOCUMENT_TO_CHECK
    })
    response.raise_for_status()
    doc_id = response.json()["document_id"]
    print(f"✅ Uploaded Document to Check. ID: {doc_id}")
    print('')
    return doc_id

# ---------- 3. Get Paragraphs ----------
def test_get_paragraphs(doc_id):
    response = requests.get(f"{BASE_URL}/document_paragraphs", params={"doc_id": doc_id})
    response.raise_for_status()
    paragraphs = response.json()
    print(f"✅ Retrieved {len(paragraphs)} Paragraphs.")
    print('')
    return paragraphs

# ---------- 4. Generate and Save Rules ----------
def test_generate_rules():
    response = requests.post(f"{BASE_URL}/generate_rules", json={"text": DOCUMENT_FOR_RULES})
    response.raise_for_status()
    rules = response.json()["rules"]
    print(f"✅ Generated and Saved {len(rules)} Rules.")
    print('')
    return rules

# ---------- 5. Get All Rules ----------
def test_get_all_rules():
    response = requests.get(f"{BASE_URL}/rules")
    response.raise_for_status()
    rules = response.json()
    print(f"✅ Retrieved {len(rules)} Rules.")
    for i, rule in enumerate(rules):
        print(f'    Rule {i}: {rule}')
    print('')
    return rules

# ---------- 6. Get Rule by ID ----------
def test_get_rule_by_id(rule_id):
    response = requests.get(f"{BASE_URL}/rules/{rule_id}")
    response.raise_for_status()
    rule = response.json()
    print(f"✅ Retrieved Rule: {rule['id']} - {rule['description']}")
    print('')
    return rule

# ---------- 7. Update Rule by ID ----------
def test_update_rule_by_id(rule_id):
    updated_data = {
        "name": "Updated Rule Title",
        "description": "Updated: All data must be encrypted at rest and in transit."
    }
    response = requests.put(f"{BASE_URL}/rules/{rule_id}", json=updated_data)
    response.raise_for_status()
    rule = response.json()
    print(f"✅ Updated Rule: {rule['id']} - {rule['description']}")
    print('')
    return rule

# ---------- 8. Check for Violation ----------
def test_check_violation(rule_id, paragraph_id):
    response = requests.post(f"{BASE_URL}/check_violation", json={
        "rule_id": rule_id,
        "paragraph_id": paragraph_id
    })
    response.raise_for_status()
    result = response.json()
    print(f"✅ Violation Checked. ID: {result['violation_id']} Text: {result['highlighted_text']}")
    print('')
    return result["violation_id"]

# ---------- 9. Suggest Fix ----------
def test_suggest_fix(violation_id):
    response = requests.post(f"{BASE_URL}/suggest_fix", params={"violation_id": violation_id})
    response.raise_for_status()
    fix = response.json()["suggested_fix"]
    print(f"✅ Suggested Fix: {fix}")
    print('')
    return fix

# ---------- 10. Accept Fix ----------
def test_accept_fix(violation_id, new_text):
    response = requests.post(f"{BASE_URL}/accept_edit", json={
        "violation_id": violation_id,
        "new_text": new_text,
        "accepted": True
    })
    response.raise_for_status()
    print("✅ Edit Accepted.")
    print('')

# ---------- 11. Get Paragraph with Neighbors ----------
def test_paragraph_neighbors(paragraph_id):
    response = requests.get(f"{BASE_URL}/paragraph_with_neighbors/{paragraph_id}")
    response.raise_for_status()
    result = response.json()
    print("✅ Paragraph with Neighbors:")
    print("   Previous:", result['previous']['content'] if result['previous'] else "None")
    print("   Current:", result['current']['content'])
    print("   Next:", result['next']['content'] if result['next'] else "None")
    print('')

# ---------- 12. General LLM Query ----------
def test_general_llm_query(prompt):
    response = requests.post(f"{BASE_URL}/llm_query", json={"prompt": prompt})
    response.raise_for_status()
    result = response.json()
    print(f"✅ General LLM Query Response:\n   Prompt: {prompt}\n   Response: {result['response']}")
    print('')
    return result["response"]

# ---------- 🚀 Run All Tests ----------
def run_all_tests():
    rules_doc_id = test_upload_for_rules()
    check_doc_id = test_upload_for_checking()
    paragraphs = test_get_paragraphs(check_doc_id)
    paragraph_id = paragraphs[1]["id"] if len(paragraphs) > 1 else paragraphs[0]["id"]

    rules = test_generate_rules()
    rule_records = test_get_all_rules()
    rule_id = rule_records[0]["id"]

    test_get_rule_by_id(rule_id)
    test_update_rule_by_id(rule_id)
    violation_id = test_check_violation(rule_id, paragraph_id)
    fix_text = test_suggest_fix(violation_id)
    test_accept_fix(violation_id, fix_text)
    test_paragraph_neighbors(paragraph_id)

    # New general LLM query test
    test_general_llm_query("What is the purpose of data encryption?")

if __name__ == "__main__":
    print("🚧 Starting API test suite...")
    time.sleep(1)
    run_all_tests()
    print("✅ All tests passed.")

