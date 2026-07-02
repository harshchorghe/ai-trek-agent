import streamlit as st
import time
from typing import Optional, Any
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

st.set_page_config(
    page_title="Explorush AI Travel Assistant",
    page_icon="🎒",
    layout="wide"
)

st.title("🎒 Explorush AI Travel Assistant")
st.markdown("Your smart travel companion for planning, packing, budget estimation, and exploring local hidden gems.")

# Load LLM with cache
@st.cache_resource
def load_model():
    try:
        model = GroqLLM(model="llama-3.1-70b-versatile", temperature=0.2)
        if model.api_key:
            return model, True
        return None, False
    except Exception:
        return None, False

llm, ollama_enabled = load_model()

# Streamlit session states
if "active_destination" not in st.session_state:
    st.session_state.active_destination = get_active_destination()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar panel
with st.sidebar:
    st.header("✈️ Trip Parameters")
    
    if st.session_state.active_destination:
        st.success(f"**Current Destination**: {st.session_state.active_destination}")
    else:
        st.warning("No active destination context. Ask a query to set it.")
        
    st.subheader("💡 Recommended Actions")
    st.info("""
    Try asking:
    - *'Plan a 4 day Goa trip'*
    - *'What is the budget for Ladakh?'*
    - *'Best cafes near Marine Drive'*
    - *'What should I pack for winter camping?'*
    - *'Is Manali safe?'*
    """)
    
    if st.button("🧹 Clear Conversation Context"):
        from tools.conversation import clear_session
        clear_session()
        st.session_state.active_destination = None
        st.session_state.chat_history = []
        st.rerun()

# User Input
user_input = st.text_input(
    "Ask anything about travel or trekking:",
    placeholder="Example: I'm planning a 4-day trip to Goa with 3 friends on a budget"
)

if st.button("Ask Assistant", type="primary") or (user_input and st.session_state.get("prev_input") != user_input):
    if user_input.strip():
        st.session_state.prev_input = user_input
        with st.spinner("Analyzing request and building travel guides..."):
            start_time = time.time()
            
            # 1. Parameter extraction
            details = extract_trip_details(user_input, llm)
            current_dest = details.get("destination")
            if not current_dest:
                trek_name = detect_trek(user_input)
                if trek_name:
                    current_dest = trek_name
                    
            if current_dest:
                set_active_destination(current_dest)
                st.session_state.active_destination = current_dest
                
            active_dest = st.session_state.active_destination
            
            # 2. Select tool
            tool = choose_tool(user_input)
            
            # 3. Process response
            response = ""
            
            if tool == "planner":
                response = create_travel_plan(user_input, llm)
            elif tool == "faq":
                faq_ans = answer_faq(user_input, llm)
                response = faq_ans if faq_ans else "I couldn't find a direct FAQ answer, but let me know what details you need!"
            elif tool == "budget":
                dest = active_dest or "Goa"
                response = estimate_budget(
                    destination=dest,
                    days=details.get("duration", 3),
                    travellers=details.get("travellers", 1),
                    style=details.get("style", "Mid-range"),
                    user_budget=details.get("budget"),
                    llm=llm
                )
            elif tool == "packing":
                dest = active_dest or ""
                response = get_packing_list(query=user_input, destination=dest, llm=llm)
            elif tool == "weather":
                if active_dest:
                    response = get_weather(active_dest)
                else:
                    response = "Please specify a destination to check the weather. E.g. 'Weather in Goa'."
            elif tool == "hotel":
                dest = active_dest or "Goa"
                response = get_hotel_recommendations(destination=dest, style=details.get("style", "Mid-range"), llm=llm)
            elif tool == "restaurant":
                dest = active_dest or "Goa"
                response = get_restaurant_recommendations(destination=dest, llm=llm)
            elif tool == "destination":
                response = recommend_destinations(user_input, llm)
            elif tool == "transport":
                dest = active_dest or "Goa"
                response = get_transportation_guidance(destination=dest, llm=llm)
            elif tool == "emergency":
                dest = active_dest or ""
                response = get_emergency_guidance(query=user_input, destination=dest, llm=llm)
            elif tool == "visa":
                response = get_visa_guidance(user_input, llm)
            elif tool == "currency":
                response = get_currency_guidance(user_input, llm)
            elif tool == "nearby":
                dest = active_dest or "Goa"
                response = get_nearby_attractions(destination=dest, llm=llm)
            elif tool == "activities":
                dest = active_dest or "Goa"
                response = get_adventure_activities(destination=dest, llm=llm)
            elif tool == "trek":
                trek_name = active_dest or "kalsubai"
                if "difficulty" in user_input.lower() or "how difficult" in user_input.lower():
                    response = f"Difficulty of {trek_name.title()}: {get_trek_difficulty(trek_name)}"
                else:
                    response = format_trek_info(trek_name)
            else:
                # Chat fallback
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

            # 4. Display result
            end_time = time.time()
            st.session_state.chat_history.append((user_input, response, tool))
            st.rerun()

# Render chat items
if st.session_state.chat_history:
    st.subheader("💬 Assistant Response")
    for user_q, ai_a, selected_tool in reversed(st.session_state.chat_history):
        with st.container():
            st.markdown(f"**👤 You**: {user_q}")
            st.markdown(f"**🤖 Explorush AI (Tool: `{selected_tool}`)**:")
            st.markdown(ai_a)
            st.divider()