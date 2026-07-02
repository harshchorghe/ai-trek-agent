import os
import sys

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from tools.llm import GroqLLM

# Import tools
from tools.conversation import (
    load_session,
    save_session,
    get_active_destination,
    set_active_destination,
    append_to_chat_history,
    get_chat_history_as_string
)
from tools.trip_details import extract_trip_details
from tools.trek import detect_trek, format_trek_info, get_trek_difficulty
from tools.planner import create_travel_plan
from tools.budget import estimate_budget
from tools.packing import get_packing_list
from tools.weather import get_weather
from tools.hotel import get_hotel_recommendations
from tools.restaurant import get_restaurant_recommendations
from tools.destination import recommend_destinations
from tools.transport import get_transportation_guidance
from tools.trip_type import get_trip_type_advice
from tools.nearby import get_nearby_attractions
from tools.currency import get_currency_guidance
from tools.emergency import get_emergency_guidance
from tools.visa import get_visa_guidance
from tools.travel_tips import get_travel_tips
from tools.events import get_cultural_events
from tools.activities import get_adventure_activities
from tools.itinerary import generate_itinerary
from tools.faq import answer_faq

# Tool Router
from tool_router import choose_tool

# We use Groq Cloud LLM with local fallback support.
try:
    llm = GroqLLM(model="llama-3.1-70b-versatile", temperature=0.2)
    # Check if Groq API key is present and test connection
    if llm.api_key:
        llm_loaded = True
        print("✅ Groq Cloud LLM (llama-3.1-70b) loaded successfully")
    else:
        llm_loaded = False
        llm = None
        print("⚠️ Groq API key missing. Running in local deterministic rule engine mode.")
except Exception as e:
    llm = None
    llm_loaded = False
    print(f"⚠️ Groq loading failed ({e}). Running in local deterministic rule engine mode.")

# ============================================================
# APPLICATION START
# ============================================================
print("\n🎒 Explorush AI Travel Assistant")
print("Type 'exit' to quit, 'clear' to reset chat history/session\n")

# Set initial destination state if any
active_dest = get_active_destination()
if active_dest:
    print(f"📌 Active Trip Destination Context: {active_dest}")

# ============================================================
# MAIN LOOP
# ============================================================
while True:
    try:
        user_input = input("You: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")
        break

    if user_input.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    if user_input.lower() == "clear":
        from tools.conversation import clear_session
        clear_session()
        print("🧹 Chat history and destination context cleared!\n")
        continue

    if not user_input:
        continue

    # 1. Update session active destination if user specifies one
    details = extract_trip_details(user_input, llm)
    current_dest = details.get("destination")
    
    # If no destination found, check for a trek name
    if not current_dest:
        trek_name = detect_trek(user_input)
        if trek_name:
            current_dest = trek_name

    if current_dest:
        set_active_destination(current_dest)
        active_dest = current_dest
    else:
        # Check active destination in session
        active_dest = get_active_destination()

    # 2. Select tool
    tool = choose_tool(user_input)
    print(f"\n[Routing to Tool: {tool} | Active Destination: {active_dest or 'None'}]\n")

    response = ""

    # ========================================================
    # TOOL ROUTING EXECUTION
    # ========================================================
    dest_required_tools = ["planner", "budget", "packing", "weather", "hotel", "restaurant", "transport", "emergency", "nearby", "activities", "trek"]
    if tool in dest_required_tools and not active_dest:
        print("Assistant: Please specify a destination or trek name so I can help you (e.g. 'plan a trip to Jaipur', 'hotels in Dubai').\n")
        continue

    if tool == "planner":
        response = create_travel_plan(user_input, llm)

    elif tool == "faq":
        faq_ans = answer_faq(user_input, llm)
        if faq_ans:
            response = faq_ans
        else:
            response = "I couldn't find a direct FAQ answer. Please let me know what travel info you need!"

    elif tool == "budget":
        response = estimate_budget(
            destination=active_dest,
            days=details.get("duration", 3),
            travellers=details.get("travellers", 1),
            style=details.get("style", "Mid-range"),
            user_budget=details.get("budget"),
            llm=llm
        )

    elif tool == "packing":
        response = get_packing_list(query=user_input, destination=active_dest, llm=llm)

    elif tool == "weather":
        response = get_weather(active_dest)

    elif tool == "hotel":
        response = get_hotel_recommendations(destination=active_dest, style=details.get("style", "Mid-range"), llm=llm)

    elif tool == "restaurant":
        response = get_restaurant_recommendations(destination=active_dest, llm=llm)

    elif tool == "destination":
        response = recommend_destinations(user_input, llm)

    elif tool == "transport":
        response = get_transportation_guidance(destination=active_dest, llm=llm)

    elif tool == "emergency":
        response = get_emergency_guidance(query=user_input, destination=active_dest, llm=llm)

    elif tool == "visa":
        response = get_visa_guidance(user_input, llm)

    elif tool == "currency":
        response = get_currency_guidance(user_input, llm)

    elif tool == "nearby":
        response = get_nearby_attractions(destination=active_dest, llm=llm)

    elif tool == "activities":
        response = get_adventure_activities(destination=active_dest, llm=llm)

    elif tool == "trek":
        # Handle trek information or difficulty
        trek_name = active_dest or "kalsubai"
        if "difficulty" in user_input.lower() or "how difficult" in user_input.lower():
            response = f"Difficulty of {trek_name.title()}: {get_trek_difficulty(trek_name)}"
        else:
            response = format_trek_info(trek_name)

    else:
        # NORMAL AI CHAT FALLBACK
        append_to_chat_history("User", user_input)
        chat_history = get_chat_history_as_string(limit=10)
        
        prompt = """You are an experienced, friendly, and professional travel consultant for Explorush.
You help users with their travel planning, destination advice, logistics, packing, budget plans, and trek queries.
Be natural, helpful, and concise. Do not sound robotic.
"""
        if active_dest:
            prompt += f"\nNote: The user is currently planning a trip to {active_dest}.\n"
            
        prompt += f"\nConversation History:\n{chat_history}\nAI:"
        
        if ollama_enabled and llm:
            try:
                response = llm.invoke(prompt)
            except Exception:
                response = "I'm having trouble connecting to my AI brain, but I'm ready to help using my travel tools. Try asking me to plan a trip, recommend places, or build a packing checklist!"
        else:
            response = "I'm currently running in offline travel mode. Try asking: 'Plan a trip to Goa', 'Recommend a budget weekend trip', 'What should I pack?', or 'Is Manali safe?'"

    # Print Response
    print(f"AI: {response}\n")

    # Record history
    if tool != "chat":
        # Also record tool replies to keep chat context rich
        append_to_chat_history("User", user_input)
        append_to_chat_history("AI", response)