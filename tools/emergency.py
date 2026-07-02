from typing import Optional, Any

SCAMS_DB = {
    "general": [
        "**The Overpriced Taxi Scam**: Drivers at airports/stations claims their meter is broken or quotes a exorbitant price. *Advice*: Use pre-paid counters, Uber/Ola, or official app rentals.",
        "**The Helpful Stranger (ATM) Scam**: Someone stands near the ATM and offers to help you avoid fees. They attempt to skim your card or view your PIN. *Advice*: Never let anyone stand near you or help you at an ATM."
    ],
    "goa": [
        "**The Cheap Jet Ski/Rental Scam**: Scooter rentals charging you for pre-existing scratches on return. *Advice*: Always take a 360-degree video of the vehicle before renting and signing any receipt.",
        "**Fake Police Scams**: Fake or corrupt local officials targeting tourists on scooters, demanding heavy cash fines for minor or made-up infractions. *Advice*: Always wear a helmet, carry valid driving documents, and ask for an official print receipt (challan)."
    ],
    "manali": [
        "**Overpriced Adventure Gear Scam**: Solang Valley vendors selling poor quality snow suits or rafting rides at double the price. *Advice*: Check official rates on tourism boards or ask at your hostel desk."
    ]
}

def get_emergency_guidance(query: str, destination: str = "", llm: Optional[Any] = None) -> str:
    text = (query + " " + destination).lower()
    
    # 1. Match destination scams
    scams = list(SCAMS_DB["general"])
    dest_name = "General Travel"
    
    if "goa" in text:
        scams.extend(SCAMS_DB["goa"])
        dest_name = "Goa"
    elif "manali" in text:
        scams.extend(SCAMS_DB["manali"])
        dest_name = "Manali"

    # 2. Helplines
    helplines = [
        "**National Emergency Number**: 112 (All-in-one emergency helpline)",
        "**Tourist Helpline**: 1363 (24/7 multi-lingual tourist assistance)",
        "**Women Helpline**: 1091",
        "**Ambulance Service**: 102 / 108"
    ]

    if llm:
        try:
            scams_list = "\n".join([f"- {s}" for s in scams])
            helpline_list = "\n".join([f"- {h}" for h in helplines])
            prompt = f"""You are a travel safety and emergency officer for Explorush.
Write an emergency, safety, and scam-awareness guide for a user traveling to: {dest_name}.
Here are the scams from our database:
{scams_list}

Here are the national helplines:
{helpline_list}

Write a professional, calm, reassuring, and highly practical guide. Keep it concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"🛡️ **Explorush Safety, Scams & Emergency Guide ({dest_name})**\n\n"
    
    output += "🚨 **Common Scams to Avoid**:\n"
    for s in scams:
        output += f"- {s}\n"
    output += "\n"
    
    output += "☎️ **Emergency Helpline Numbers (India)**:\n"
    for h in helplines:
        output += f"- {h}\n"
        
    output += "\n💡 *Safety Tip*: Always save your travel insurance policy offline on your phone and share your hotel address/contact with at least one friend back home."
    return output
