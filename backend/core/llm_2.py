# backend/core/llm.py
from litellm import completion

def check_violation(paragraph: str, rule: str) -> str:
    prompt = f"Does the following paragraph violate the rule '{rule}'? If so, identify the problematic text:\n\n{paragraph}"
    response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    return response['choices'][0]['message']['content']

def suggest_fix(text: str, rule: str) -> str:
    prompt = f"Given the following rule '{rule}', suggest an improved version of this text:\n\n{text}"
    response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    return response['choices'][0]['message']['content']
