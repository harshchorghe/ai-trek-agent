def extract_location(user_input, llm):

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