import os
import sys
import requests
from pymongo import MongoClient

# UTF-8 encoding configuration
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MONGODB_URI = os.getenv("MONGODB_URI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("🔍 EXPLORUSH DIAGNOSTICS TOOL\n")
print(f"Project Working Directory: {os.getcwd()}")
print(f"MongoDB URI present: {'Yes' if MONGODB_URI else 'No'}")
print(f"Groq API Key present: {'Yes' if GROQ_API_KEY else 'No'}\n")

# ============================================================
# 1. TEST GROQ CONNECTION
# ============================================================
if GROQ_API_KEY:
    print("Testing connection to Groq API...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "Hello! Confirm connection."}],
        "max_tokens": 50
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=8)
        if response.status_code == 200:
            print("✅ Groq API connected successfully!")
            print(f"Response: {response.json()['choices'][0]['message']['content'].strip()}\n")
        else:
            print(f"❌ Groq API failed with status {response.status_code}")
            print(f"Error Details: {response.text}\n")
    except Exception as e:
        print(f"❌ Groq API failed to connect: {e}\n")
else:
    print("ℹ️ Skipping Groq test (API Key missing in .env)\n")

# ============================================================
# 2. TEST MONGODB ATLAS CONNECTION
# ============================================================
if MONGODB_URI:
    print("Testing connection to MongoDB Atlas...")
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Force ping
        client.admin.command('ping')
        print("✅ MongoDB Atlas connected successfully!")
        db = client.explorush_db
        collections = db.list_collection_names()
        print(f"Available Collections in 'explorush_db': {collections}\n")
    except Exception as e:
        print(f"❌ MongoDB Atlas failed to connect: {e}\n")
else:
    print("ℹ️ Skipping MongoDB test (URI missing in .env)\n")
