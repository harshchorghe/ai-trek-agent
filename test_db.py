import sys
import json

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from tools.trip_details import extract_trip_details

print("🧪 Explorush Parameter Extraction Test Utility")
print("Type a trip description to see extracted details. Type 'exit' to quit.\n")

while True:
    try:
        text = input("Message: ").strip()
    except (KeyboardInterrupt, EOFError):
        break
        
    if text.lower() == "exit":
        break
        
    if not text:
        continue
        
    # Test deterministic & LLM extraction (offline test, so LLM=None)
    details = extract_trip_details(text, llm=None)
    
    print("\nExtracted Parameters:")
    print(json.dumps(details, indent=2))
    print()