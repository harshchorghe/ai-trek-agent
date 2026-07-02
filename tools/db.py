import os
import json
import time
from typing import Optional, Dict, Any

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# MongoDB URI from .env
MONGODB_URI = os.getenv("MONGODB_URI")
LOCAL_CACHE_FILE = "data/travel_cache.json"

# Connect to MongoDB Atlas (if URI is configured)
db_client = None
db = None
mongo_available = False

if MONGODB_URI:
    try:
        from pymongo import MongoClient
        # Set a short 3-second connection timeout so the app doesn't freeze if database is offline
        db_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        # Ping the server to trigger connection check
        db_client.admin.command('ping')
        db = db_client.explorush_db
        mongo_available = True
        print("✅ MongoDB Atlas connected successfully")
    except Exception as e:
        print(f"⚠️ MongoDB connection failed ({e}). Falling back to local JSON cache.")
        mongo_available = False
else:
    print("ℹ️ No MONGODB_URI found in environment. Using local JSON cache.")

# ============================================================
# LOCAL JSON FILE CACHE FALLBACK LOGIC
# ============================================================
def _load_local_cache() -> Dict[str, Any]:
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(LOCAL_CACHE_FILE):
        try:
            with open(LOCAL_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_local_cache(cache: Dict[str, Any]):
    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        with open(LOCAL_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"Error saving local cache file: {e}")

def _generate_composite_key(destination: str, duration: int, travellers: int, style: str) -> str:
    # Key format: destination_duration_travellers_style
    return f"{destination.lower().strip()}_{duration}_{travellers}_{style.lower().strip()}"

# ============================================================
# PUBLIC INTERFACE FOR CACHING
# ============================================================
def get_cached_plan(destination: str, duration: int, travellers: int, style: str) -> Optional[str]:
    dest_clean = destination.lower().strip()
    style_clean = style.lower().strip()

    # 1. Try Mongo
    if mongo_available and db is not None:
        try:
            plan = db.plans.find_one({
                "destination": dest_clean,
                "duration": duration,
                "travellers": travellers,
                "style": style_clean
            })
            if plan:
                print("🎯 Cache Hit: Loaded plan from MongoDB Atlas Cloud")
                return plan.get("plan_text")
        except Exception as e:
            print(f"Database error during fetch ({e}). Trying local cache fallback.")

    # 2. Try Local Fallback Cache
    key = _generate_composite_key(dest_clean, duration, travellers, style_clean)
    local_cache = _load_local_cache()
    if key in local_cache:
        print("🎯 Cache Hit: Loaded plan from local JSON file")
        return local_cache[key]

    return None

def save_plan_to_cache(destination: str, duration: int, travellers: int, style: str, plan_text: str):
    dest_clean = destination.lower().strip()
    style_clean = style.lower().strip()

    # 1. Try Save to Mongo
    saved_in_mongo = False
    if mongo_available and db is not None:
        try:
            # Upsert (update if exists, insert if new)
            db.plans.update_one(
                {
                    "destination": dest_clean,
                    "duration": duration,
                    "travellers": travellers,
                    "style": style_clean
                },
                {
                    "$set": {
                        "destination": dest_clean,
                        "duration": duration,
                        "travellers": travellers,
                        "style": style_clean,
                        "plan_text": plan_text,
                        "updated_at": time.time()
                    }
                },
                upsert=True
            )
            print("💾 Saved plan to MongoDB Atlas Cloud")
            saved_in_mongo = True
        except Exception as e:
            print(f"Database error during save ({e}).")

    # 2. Always write to Local JSON Cache as a safety double-save
    key = _generate_composite_key(dest_clean, duration, travellers, style_clean)
    local_cache = _load_local_cache()
    local_cache[key] = plan_text
    _save_local_cache(local_cache)
    print("💾 Saved plan to local JSON file")

def get_cached_item(category: str, key: str) -> Optional[str]:
    key_clean = key.lower().strip()
    # 1. Try Mongo
    if mongo_available and db is not None:
        try:
            item = db[category].find_one({"key": key_clean})
            if item:
                print(f"🎯 Cache Hit: Loaded {category} from MongoDB Atlas ({key_clean})")
                return item.get("value")
        except Exception as e:
            print(f"Database error fetching cached {category} ({e})")

    # 2. Try Local fallback
    local_cache = _load_local_cache()
    local_key = f"{category}_{key_clean}"
    if local_key in local_cache:
        print(f"🎯 Cache Hit: Loaded {category} from local JSON file ({key_clean})")
        return local_cache[local_key]
    return None

def save_cached_item(category: str, key: str, value: str):
    key_clean = key.lower().strip()
    # 1. Try Mongo
    if mongo_available and db is not None:
        try:
            db[category].update_one(
                {"key": key_clean},
                {"$set": {
                    "key": key_clean,
                    "value": value,
                    "updated_at": time.time()
                }},
                upsert=True
            )
            print(f"💾 Saved {category} to MongoDB Atlas ({key_clean})")
        except Exception as e:
            print(f"Database error saving {category} ({e})")

    # 2. Local fallback
    local_cache = _load_local_cache()
    local_key = f"{category}_{key_clean}"
    local_cache[local_key] = value
    _save_local_cache(local_cache)
    print(f"💾 Saved {category} to local JSON file ({key_clean})")
