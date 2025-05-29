import requests

def edit_text_with_llm(text: str, instruction: str):
    response = requests.post("http://ollama:11434/api/generate", json={
        "model": "llama3",
        "prompt": instruction + "\n\n" + text
    })
    return response.json()["response"]