import os
import json
import time
import re
from typing import Optional, Dict, Any, List
from tools.cache_config import CACHE_EXPIRY

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# MongoDB URI from .env
MONGODB_URI = os.getenv("MONGODB_URI")
LOCAL_KB_FILE = "data/destination_kb.json"

db_client = None
db = None
mongo_available = False

if MONGODB_URI:
    try:
        from pymongo import MongoClient
        # Set a short 3-second connection timeout
        db_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        db_client.admin.command('ping')
        db = db_client.explorush_db
        mongo_available = True
        
        # Ensure database indices for high performance lookups
        db.destinations.create_index("normalizedDestination", unique=True)
        print("[MongoDB] Connected successfully. Index created on normalizedDestination.")
    except Exception as e:
        print(f"[MongoDB] Connection failed ({e}). Falling back to local JSON Knowledge Base.")
        mongo_available = False
else:
    print("[MongoDB] No MONGODB_URI found. Using local JSON Knowledge Base.")

# ============================================================
# NORMALIZATION UTILITY
# ============================================================
def normalize_destination(destination: str) -> str:
    """
    Cleans and standardizes destination names for high-frequency cache matching.
    Example: 'Mount Abu ' -> 'mount_abu'
             'Ujjain Junction' -> 'ujjain'
    """
    if not destination:
        return ""
    text = destination.lower().strip()
    
    # Strip common trailing suffix keywords that are parts of station/airport names
    text = re.sub(r'\b(junction|airport|station|terminal|city|town|village|beach|hills)\b', '', text).strip()
    
    # Replace spaces, hyphens, and slashes with underscores
    text = re.sub(r'[\s\-\/]+', '_', text)
    
    # Remove any non-alphanumeric character (except underscores)
    text = re.sub(r'[^a-z0-9_]', '', text)
    
    return text.strip("_")

# ============================================================
# LOCAL JSON FILE KB FALLBACK LOGIC
# ============================================================
def _load_local_kb() -> Dict[str, Any]:
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(LOCAL_KB_FILE):
        try:
            with open(LOCAL_KB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_local_kb(kb: Dict[str, Any]):
    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        with open(LOCAL_KB_FILE, "w", encoding="utf-8") as f:
            json.dump(kb, f, indent=2)
    except Exception as e:
        print(f"Error saving local Knowledge Base file: {e}")

# ============================================================
# PUBLIC INTERFACE FOR KNOWLEDGE BASE
# ============================================================
def get_cached_item(category: str, destination: str) -> Optional[str]:
    """
    Looks up a specific knowledge section for a destination.
    Updates hitCount and lastAccessed timestamps on a cache hit.
    """
    dest_norm = normalize_destination(destination)
    if not dest_norm:
        return None
        
    current_time = time.time()

    # 1. Try Mongo
    if mongo_available and db is not None:
        try:
            doc = db.destinations.find_one({"normalizedDestination": dest_norm})
            if doc and "sections" in doc and category in doc["sections"]:
                section = doc["sections"][category]
                
                # Check Expiry
                expiry = section.get("expiry")
                updated_at = section.get("updatedAt", 0)
                if expiry is not None and (current_time - updated_at) > expiry:
                    print(f"Cache Expired: {category} for {dest_norm} is stale.")
                    return None
                
                # Update stats: increment hitCount, set lastAccessed
                db.destinations.update_one(
                    {"normalizedDestination": dest_norm},
                    {
                        "$inc": {
                            "totalHits": 1,
                            f"sections.{category}.hitCount": 1
                        },
                        "$set": {
                            "lastAccessed": current_time,
                            f"sections.{category}.lastAccessed": current_time
                        }
                    }
                )
                print(f"KB Hit (Mongo): {category} for {dest_norm}")
                return section.get("response")
        except Exception as e:
            print(f"Database error during KB lookup: {e}")

    # 2. Try Local Fallback JSON
    local_kb = _load_local_kb()
    if dest_norm in local_kb:
        doc = local_kb[dest_norm]
        if "sections" in doc and category in doc["sections"]:
            section = doc["sections"][category]
            
            # Check Expiry
            expiry = section.get("expiry")
            updated_at = section.get("updatedAt", 0)
            if expiry is not None and (current_time - updated_at) > expiry:
                print(f"Local Cache Expired: {category} for {dest_norm} is stale.")
                return None
                
            # Update stats
            doc["totalHits"] = doc.get("totalHits", 0) + 1
            doc["lastAccessed"] = current_time
            section["hitCount"] = section.get("hitCount", 0) + 1
            section["lastAccessed"] = current_time
            
            _save_local_kb(local_kb)
            print(f"KB Hit (Local JSON): {category} for {dest_norm}")
            return section.get("response")

    return None

def save_cached_item(category: str, destination: str, value: str, source: str = "groq"):
    """
    Saves a specific knowledge section inside the unified destination document.
    Never overwrites other pre-existing sections.
    """
    dest_norm = normalize_destination(destination)
    if not dest_norm or not value:
        return
        
    current_time = time.time()
    expiry_time = CACHE_EXPIRY.get(category)
    
    section_doc = {
        "response": value.strip(),
        "createdAt": current_time,
        "updatedAt": current_time,
        "lastAccessed": current_time,
        "hitCount": 1,
        "source": source,
        "version": "1.0",
        "expiry": expiry_time
    }

    # 1. Try Save to Mongo
    if mongo_available and db is not None:
        try:
            # Perform upsert to create/update destination with this section
            db.destinations.update_one(
                {"normalizedDestination": dest_norm},
                {
                    "$set": {
                        "destination": destination.strip(),
                        "normalizedDestination": dest_norm,
                        "lastUpdated": current_time,
                        "lastAccessed": current_time,
                        f"sections.{category}": section_doc
                    },
                    "$setOnInsert": {
                        "createdAt": current_time,
                        "totalHits": 0
                    }
                },
                upsert=True
            )
            # Increment totalHits for this access write
            db.destinations.update_one(
                {"normalizedDestination": dest_norm},
                {"$inc": {"totalHits": 1}}
            )
            print(f"KB Save (Mongo): Saved {category} for {dest_norm}")
        except Exception as e:
            print(f"Database error during KB save: {e}")

    # 2. Always write to Local JSON Cache as a safety double-save
    local_kb = _load_local_kb()
    if dest_norm not in local_kb:
        local_kb[dest_norm] = {
            "destination": destination.strip(),
            "normalizedDestination": dest_norm,
            "totalHits": 0,
            "createdAt": current_time,
            "lastUpdated": current_time,
            "lastAccessed": current_time,
            "sections": {}
        }
    
    doc = local_kb[dest_norm]
    doc["lastUpdated"] = current_time
    doc["lastAccessed"] = current_time
    doc["totalHits"] += 1
    doc["sections"][category] = section_doc
    
    _save_local_kb(local_kb)
    print(f"KB Save (Local JSON): Saved {category} for {dest_norm}")

# ============================================================
# CACHE ANALYTICS HELPER
# ============================================================
def get_popular_destinations(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Returns ranking of the most searched travel destinations.
    """
    # 1. Try Mongo
    if mongo_available and db is not None:
        try:
            cursor = db.destinations.find(
                {}, 
                {"destination": 1, "normalizedDestination": 1, "totalHits": 1}
            ).sort("totalHits", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"Database error during analytics: {e}")

    # 2. Local Fallback
    local_kb = _load_local_kb()
    items = [
        {
            "destination": val["destination"],
            "normalizedDestination": val["normalizedDestination"],
            "totalHits": val["totalHits"]
        }
        for val in local_kb.values()
    ]
    items.sort(key=lambda x: x["totalHits"], reverse=True)
    return items[:limit]
