from typing import Optional, Any

def get_visa_guidance(query: str, llm: Optional[Any] = None) -> str:
    text = query.lower()
    
    dest = "General Outbound"
    requirements = [
        "A passport valid for at least 6 months from the date of entry with 2 empty pages.",
        "A return or onward flight ticket and proof of sufficient funds.",
        "Confirmed hotel bookings matching the duration of your visa request.",
        "Check if you require an eVisa or Visa on Arrival (VoA)."
    ]

    # Specific countries
    if any(word in text for word in ["nepal", "bhutan"]):
        dest = "Nepal & Bhutan"
        requirements = [
            "Indian citizens do not require a visa to enter Nepal or Bhutan.",
            "You must carry a valid Indian Passport or voter identity card issued by the Election Commission of India.",
            "Other documents like Aadhaar card or driving licenses are NOT official travel documents for Nepal/Bhutan entry."
        ]
    elif any(word in text for word in ["thailand", "bangkok"]):
        dest = "Thailand"
        requirements = [
            "Visa-free entry for Indian citizens is often updated seasonally (please verify current tourism policies).",
            "Normally, Visa on Arrival (VoA) is available at major airports for up to 15 days for a fee of 2000 THB.",
            "You must carry at least 10,000 THB per person (or equivalent in USD/INR) as proof of cash funds on entry.",
            "A physical passport-sized photo (4x6 cm) with white background is required for VoA."
        ]
    elif any(word in text for word in ["europe", "france", "germany", "italy", "schengen"]):
        dest = "Schengen Area (Europe)"
        requirements = [
            "You must apply for a Schengen Visa (Type C Short Stay) via VFS Global at least 15-45 days before departure.",
            "Requires comprehensive Travel Medical Insurance covering at least €30,000.",
            "Requires detailed day-wise itinerary, flight tickets (dummy or confirmed depending on consulate), and hotel vouchers.",
            "Requires 3-6 months bank statement showing stable income and strong financial ties to India."
        ]
    elif any(word in text for word in ["vietnam", "hanoi"]):
        dest = "Vietnam"
        requirements = [
            "Indian citizens require an eVisa in advance.",
            "Apply via the official Vietnam Immigration Portal at least 3-5 working days prior.",
            "eVisa fee is approx $25 USD (single entry) or $50 USD (multiple entry).",
            "Ensure the spelling of your name on the eVisa exactly matches your passport passport machine-readable zone (MRZ)."
        ]

    if llm:
        try:
            req_list = "\n".join([f"- {r}" for r in requirements])
            prompt = f"""You are a visa and immigration specialist for Explorush.
Write a friendly, informative, and professional visa guidance summary for travel to: {dest}.
Requirements database:
{req_list}

Remind the user that visa policies change frequently and they should always check official embassy portals. Keep it concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"🛂 **Explorush Visa Information Guide ({dest})**\n\n"
    output += "📌 **Key Travel Requirements**:\n"
    for r in requirements:
        output += f"- {r}\n"
        
    output += "\n⚠️ *Important Disclaimer*: Visa and entry policies are subject to change. Always verify the latest guidelines with the official embassy or consulate website before booking travel!"
    return output
