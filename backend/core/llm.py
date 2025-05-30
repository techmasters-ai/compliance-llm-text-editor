# backend/core/llm.py
from fastapi import HTTPException
import os, json, requests
import imaplib
import base64
import mimetypes
import re

def clean_your_string(text_str):
    results = []
    # Split response into lines and process each 'data: ' line
    for line in text_str.splitlines():
        line = line.strip()
        if line.startswith('data: ') and line != 'data: [DONE]':
            try:
                json_str = line.replace('data: ', '', 1)
                parsed = json.loads(json_str)
                content = parsed['choices'][0]['delta'].get('content')
                if content:
                    results.append(content)
            except json.JSONDecodeError as e:
                print(f"Failed to decode line: {line}\nError: {e}")
    
    # Join content parts and strip markdown formatting
    full_content = ''.join(results)
    content = re.sub(r'^```json\n|```$', '', full_content.strip(), flags=re.MULTILINE)

    return content

def create_image_data(image_path: str):
    """
    Prepares a structured API payload including a base64-encoded image.

    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: Two required fields to construct payload.
    """
    # Determine the MIME type
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        raise ValueError("Unsupported or unknown file type")

    # Read and encode the image in base64
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
    return {'mime_type': mime_type, 'encoded_image': encoded_image}

def create_text_only_payload(prompt, model):

    # Define the request body (JSON payload)
    payload = {
        "model": model ,
        "messages": [{"role": "user", "content": prompt}]
        }
    return payload

def create_text_and_image_payload(prompt, image_path, model):
    image_data_dict = create_image_data(image_path)
    # Define the request body (JSON payload)
    payload = {
                "model": model,
                "messages": [
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": prompt
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_data_dict['mime_type']};base64,{image_data_dict['encoded_image']}"
                        }
                        }
                    ]
                }
            ]
        } 
    return payload

def call_llm(payload, owui_user_api_key):
    OWUI_BASE_URL = os.getenv("OWUI_BASE_URL")

    # Define the API endpoint and the JWT btoken
    url = f"{OWUI_BASE_URL}/api/chat/completions"

    # Define the request headers
    headers = {
        "Authorization": f"Bearer {owui_user_api_key}",
        "Content-Type": "application/json"
    }

    # Send the POST request
    resp = requests.post(url, headers=headers, json=payload)
    try:
        content = resp.json()['choices'][0]['message']['content']
    except:
        content = clean_your_string(resp.text)

    return content


def general_llm_query(query):

    MODEL_NAME = os.getenv("MODEL_NAME")
    OWUI_API_KEY = os.getenv("OWUI_API_KEY")
    payload = create_text_only_payload(query, MODEL_NAME)

    try:
        result = call_llm(payload, OWUI_API_KEY)
        return {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")



def check_violation(paragraph: str, rule: str) -> str:
    MODEL_NAME = os.getenv("MODEL_NAME") 
    OWUI_API_KEY = os.getenv("OWUI_API_KEY")

    prompt = f"Does the following paragraph violate the rule '{rule}'? If so, identify the problematic text:\n\n{paragraph}"

    payload = create_text_only_payload(prompt, MODEL_NAME)

    try:
        result = call_llm(payload, OWUI_API_KEY)
        return result  # ✅ return raw string, not {"response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")



def suggest_fix(text: str, rule: str) -> str:
    MODEL_NAME = os.getenv("MODEL_NAME") 
    OWUI_API_KEY = os.getenv("OWUI_API_KEY")

    prompt = f"""Given the following issues identified in a paragraph:\n\n{rule}
                 Here is the original paragraph:{text}
                 Rewrite the paragraph to address all the issues above. Return only the improved version of the paragraph. 
             """


    payload = create_text_only_payload(prompt, MODEL_NAME)

    try:
        result = call_llm(payload, OWUI_API_KEY)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")


def generate_compliance_rules(text: str) -> list[str]:
    MODEL_NAME = os.getenv("MODEL_NAME") 
    OWUI_API_KEY = os.getenv("OWUI_API_KEY")
    
    prompt = f"""You are a compliance officer. Given the following policy document or guideline, extract a concise list of explicit compliance rules.
    Each rule should be clear, actionable, and self-contained. Only return the rules, no other text. Return the rules as a list (one per line). 

    Document:
    {text}

    Compliance Rules:"""

    payload = create_text_only_payload(prompt, MODEL_NAME)

    try:
        raw_output = call_llm(payload, OWUI_API_KEY)
        result = [line.strip() for line in raw_output.split('\n') if line.strip()]
        return result  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM query failed: {str(e)}")
