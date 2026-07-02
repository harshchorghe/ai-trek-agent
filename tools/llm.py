import os
import requests
from typing import Optional, Dict, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class GroqLLM:
    """
    Lightweight, dependency-free wrapper for Groq Cloud completions API.
    Emulates the standard langchain invoke() interface.
    """
    def __init__(self, model: str = "llama-3.3-70b-versatile", temperature: float = 0.2, max_tokens: int = 1024):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            print("⚠️ GROQ_API_KEY not found in environment. The AI agent will fall back to local rule-based responses.")

    def invoke(self, prompt: str) -> Optional[str]:
        if not self.api_key:
            return None
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            # Set a 12-second timeout
            response = requests.post(url, headers=headers, json=data, timeout=12)
            response.raise_for_status()
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"⚠️ Groq API request failed ({e}). Falling back to local tool engines.")
            return None
