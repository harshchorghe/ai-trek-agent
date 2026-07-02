from tools.trip_details import extract_trip_details

def extract_location(user_input, llm=None):
    # Try the new detailed extraction first
    details = extract_trip_details(user_input, llm)
    if details.get("destination"):
        return details["destination"]
        
    if llm:
        prompt = f"""
Extract only the trek/location name.

Examples:

Input: Plan a trek to Harishchandragad
Output: Harishchandragad

Input: Weather at Ratangad
Output: Ratangad

Input: I want to trek Kunjargad next weekend
Output: Kunjargad

Input: {user_input}
Output:
"""
        return llm.invoke(prompt).strip()
        
    return user_input.strip()