import os
import json
import sys
from pymongo import MongoClient

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    print("❌ Error: MONGODB_URI not found in your .env file!")
    print("Please make sure you have created the .env file in the root directory containing your MongoDB connection string.")
    sys.exit(1)

print("🔗 Connecting to MongoDB Atlas...")

try:
    # Set a short 5-second timeout for server selection
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Trigger connection check
    client.admin.command('ping')
    
    # Use database "explorush_db"
    db = client.explorush_db
    print("✅ Connected to MongoDB Atlas successfully.\n")
    
    # --------------------------------------------------------
    # 1. IMPORT TREKS
    # --------------------------------------------------------
    treks_path = "data/treks.json"
    if os.path.exists(treks_path):
        print(f"Reading {treks_path}...")
        with open(treks_path, "r", encoding="utf-8") as f:
            treks_data = json.load(f)
            
        documents = []
        for name, info in treks_data.items():
            doc = {
                "name": name,
                "difficulty": info.get("difficulty"),
                "duration": info.get("duration"),
                "height": info.get("height")
            }
            documents.append(doc)
            
        if documents:
            # Clear existing collection and insert fresh
            db.treks.delete_many({})
            db.treks.insert_many(documents)
            print(f"📤 Successfully imported {len(documents)} treks into the 'treks' collection.")
    else:
        print("ℹ️ No treks.json file found to import.")
        
    # --------------------------------------------------------
    # 2. IMPORT CACHED PLANS (If any exist)
    # --------------------------------------------------------
    cache_path = "data/travel_cache.json"
    if os.path.exists(cache_path):
        print(f"Reading {cache_path}...")
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
            
        documents = []
        for key, plan_text in cache_data.items():
            parts = key.split("_")
            if len(parts) >= 4:
                try:
                    doc = {
                        "destination": parts[0],
                        "duration": int(parts[1]),
                        "travellers": int(parts[2]),
                        "style": parts[3],
                        "plan_text": plan_text
                    }
                    documents.append(doc)
                except ValueError:
                    pass
                    
        if documents:
            db.plans.delete_many({})
            db.plans.insert_many(documents)
            print(f"📤 Successfully imported {len(documents)} cached plans into the 'plans' collection.")
    else:
        print("ℹ️ No local cache file (travel_cache.json) found to import. A new one will start when you run a query.")

    print("\n🎉 Import complete! Open your MongoDB Atlas dashboard and click the 'Refresh' button.")
    print("You should now see the 'explorush_db' database with your collections ('treks' and 'plans')!")

except Exception as e:
    print(f"❌ Connection or import failed: {e}")
    sys.exit(1)
