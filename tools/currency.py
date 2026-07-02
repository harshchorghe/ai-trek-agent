from typing import Optional, Any

def get_currency_guidance(query: str, llm: Optional[Any] = None) -> str:
    text = query.lower()
    
    # Check for international destinations
    dest = "General"
    currency_name = "INR (Indian Rupee)"
    symbol = "₹"
    tips = [
        "In India, cash is king, especially in rural areas, base villages of treks, and street food stalls.",
        "Ensure you carry smaller denominations (₹10, ₹20, ₹50, ₹100, ₹200) for local travel, tolls, and village entries.",
        "UPI digital payments (GPay, PhonePe, Paytm) are widely accepted across India, even at tiny stalls, but internet connectivity can fail in remote hills.",
        "Credit cards are accepted at all mid-to-high-end hotels, resorts, and restaurants."
    ]

    # Custom destinations
    if any(word in text for word in ["nepal", "everest", "annapurna"]):
        dest = "Nepal"
        currency_name = "NPR (Nepalese Rupee)"
        symbol = "₨"
        tips = [
            "Indian Rupees (except ₹500 and ₹2000 notes) are widely accepted in Nepal.",
            "You can easily exchange INR for NPR at the border town or in Kathmandu.",
            "Carry cash on treks (like Everest Base Camp or Annapurna Circuit)—ATMs are rare and charge high transaction fees.",
            "International credit cards are accepted in major Kathmandu and Pokhara hotels."
        ]
    elif any(word in text for word in ["europe", "france", "germany", "italy", "spain", "switzerland"]):
        dest = "Europe"
        currency_name = "EUR (Euro)"
        symbol = "€"
        tips = [
            "Card payments are dominant in Western Europe. Carry a zero-forex credit/debit card.",
            "Always choose to pay in the local currency (EUR) at POS machines instead of INR to avoid dynamic currency markup fees (DCC).",
            "Carry small amounts of Euro cash for public toilets, luggage lockers, and minor bakeries.",
            "For Switzerland, CHF (Swiss Franc) is used. Keep some CHF cash handy if crossing borders."
        ]
    elif any(word in text for word in ["thailand", "bangkok", "phuket"]):
        dest = "Thailand"
        currency_name = "THB (Thai Baht)"
        symbol = "฿"
        tips = [
            "Thailand is highly cash-oriented. Carry THB cash for street markets, taxis, and entry fees.",
            "Local ATMs charge a flat fee of approx. 220 THB (~₹500) per withdrawal. It is better to withdraw larger amounts at once.",
            "Currency booths (like SuperRich) in Bangkok offer excellent exchange rates for cash INR/USD.",
            "Ensure bills are crisp and uncreased when exchanging physical currency."
        ]

    if llm:
        try:
            tips_list = "\n".join([f"- {t}" for t in tips])
            prompt = f"""You are a financial travel advisor for Explorush.
Write a friendly guide on currency and money tips for travelers visiting: {dest}.
Currency: {currency_name} ({symbol})
Core tips:
{tips_list}

Keep it professional, helpful, and concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"💵 **Explorush Currency & Money Guide ({dest})**\n"
    output += f"💳 **Official Currency**: {currency_name} ({symbol})\n\n"
    output += "📌 **Money Tips & Exchange Advice**:\n"
    for tip in tips:
        output += f"- {tip}\n"
        
    output += "\n💡 *Forex Tip*: Avoid exchanging currency at airport counters; they charge the highest commissions (up to 15%). Buy a multi-currency Forex card in advance!"
    return output
