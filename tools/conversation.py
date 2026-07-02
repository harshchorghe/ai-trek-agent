import os
import json
from typing import List, Dict, Optional, Any

SESSION_FILE = "memory/session.json"
MEMORY_FILE = "memory/chat_history.txt"

def load_session() -> Dict[str, Any]:
    if not os.path.exists("memory"):
        os.makedirs("memory")
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active_destination": None, "messages": []}

def save_session(session_data: Dict[str, Any]):
    if not os.path.exists("memory"):
        os.makedirs("memory")
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
    except Exception as e:
        print(f"Error saving session: {e}")

def get_active_destination() -> Optional[str]:
    session = load_session()
    return session.get("active_destination")

def set_active_destination(destination: str):
    session = load_session()
    session["active_destination"] = destination
    save_session(session)

def clear_session():
    session = {"active_destination": None, "messages": []}
    save_session(session)
    if os.path.exists(MEMORY_FILE):
        try:
            os.remove(MEMORY_FILE)
        except Exception:
            pass

def append_to_chat_history(role: str, content: str):
    # Standard format: Role: Content
    message_line = f"{role}: {content}"
    
    # Save to text memory file
    try:
        with open(MEMORY_FILE, "a", encoding="utf-8") as file:
            file.write(message_line + "\n")
    except Exception as e:
        print(f"Error writing to chat history file: {e}")
        
    # Also save in session JSON
    session = load_session()
    if "messages" not in session:
        session["messages"] = []
    session["messages"].append({"role": role.lower(), "content": content})
    # Keep only last 12 messages in session
    session["messages"] = session["messages"][-12:]
    save_session(session)

def get_chat_history_as_string(limit: int = 12) -> str:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
                return "\n".join(lines[-limit:])
        except Exception:
            pass
    
    # Fallback to session JSON
    session = load_session()
    lines = []
    for msg in session.get("messages", [])[-limit:]:
        role_label = "User" if msg["role"] == "user" else "AI"
        lines.append(f"{role_label}: {msg['content']}")
    return "\n".join(lines)
