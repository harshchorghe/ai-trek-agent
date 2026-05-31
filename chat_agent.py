from langchain_ollama import OllamaLLM
from collections import deque

from tools.trek_detector import detect_trek
from tools.trek_info import format_trek_info

from tools.planner import create_trek_plan

# ============================================================
# TOOLS
# ============================================================

from tools.packing import get_packing_list
from tools.difficulty import get_trek_difficulty
from tools.itinerary import generate_itinerary
from tools.weather import get_weather

# ============================================================
# TOOL ROUTER
# ============================================================

from tool_router import choose_tool

# ============================================================
# MEMORY CONFIGURATION
# ============================================================

MEMORY_FILE = "memory/chat_history.txt"

# ============================================================
# LLM CONFIGURATION
# ============================================================

llm = OllamaLLM(
    model="phi3",
    temperature=0.2,
    num_predict=180,
    keep_alive="30m",
)

# ============================================================
# CONVERSATION MEMORY
# ============================================================

conversation = deque(maxlen=12)

# Load previous chat history
try:
    with open(MEMORY_FILE, "r", encoding="utf-8") as file:

        lines = file.readlines()

        for line in lines[-12:]:
            conversation.append(line.strip())

    print("✅ Previous memory loaded")

except FileNotFoundError:
    print("⚠️ No previous memory found")

# ============================================================
# APPLICATION START
# ============================================================

print("\n🥾 AI Trek Planner")
print("Type 'exit' to quit\n")

# ============================================================
# MAIN CHAT LOOP
# ============================================================

while True:

    user_input = input("You: ").strip()

    # Exit application
    if user_input.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    # Ignore empty input
    if not user_input:
        continue

    # ========================================================
    # TOOL SELECTION
    # ========================================================

    tool = choose_tool(user_input)

    print(f"\n[Selected Tool: {tool}]\n")
    # ========================================================
    # TOOL 1 : PACKING LIST
    # ========================================================

    if tool == "packing":

        print("\nAI:", get_packing_list())
        print()

        continue

    # ========================================================
    # TOOL 2 : TREK DIFFICULTY
    # ========================================================

    elif tool == "difficulty":

        trek_name = detect_trek(user_input)

        if not trek_name:
            trek_name = input(
                "Enter Trek Name: "
            ).strip()

        print(
            "\nAI:",
            get_trek_difficulty(trek_name)
        )

        print()

        continue

    # ========================================================
    # TOOL 3 : ITINERARY GENERATOR
    # ========================================================

    elif tool == "itinerary":

        print(
            "\nAI:",
            generate_itinerary()
        )

        print()

        continue

    # ========================================================
    # TOOL 4 : WEATHER INFORMATION
    # ========================================================

    elif tool == "weather":

        trek_name = detect_trek(user_input)

        if not trek_name:
            trek_name = input(
                "Enter Trek Location: "
            ).strip()

        print(
            "\nAI:",
            get_weather(trek_name)
        )

        print()

        continue

    # ========================================================
    # TOOL 5 : TREK PLANNER
    # ========================================================

    elif tool == "planner":

        trek_name = detect_trek(user_input)

        if not trek_name:
            trek_name = input(
                "Enter Trek Location: "
            ).strip()

        print(
            f"\nDetected Trek: {trek_name}"
        )

        print(
            "\nAI:",
            create_trek_plan(trek_name)
        )

        print()

        continue

    # ========================================================
    # TOOL 6 : TREK INFORMATION
    # ========================================================

    elif tool == "trek_info":

        trek_name = detect_trek(user_input)

        if trek_name:

            print(
                "\nAI:",
                format_trek_info(trek_name)
            )

        else:

            print(
                "\nAI: Trek not found in database."
            )

        print()

        continue
 # ========================================================
# TOOL : TREK INFORMATION
# ========================================================

    elif tool == "trek_info":

        trek_name = detect_trek(user_input)

    if trek_name:

        print(
            "\nAI:",
            format_trek_info(trek_name)
        )

    else:

        print(
            "\nAI: Trek not found in database."
        )

    print()

    continue


    # ========================================================
     

    # NORMAL AI CHAT
    # ========================================================

    user_message = f"User: {user_input}"

    conversation.append(user_message)

    # Save user message
    with open(MEMORY_FILE, "a", encoding="utf-8") as file:
        file.write(user_message + "\n")

    prompt = """
You are TrekGPT, an expert trekking guide from Maharashtra.

You help users with:
- Trek recommendations
- Trek planning
- Packing advice
- Safety tips
- Weather preparation

Give practical and concise answers.
"""

    prompt += "\n".join(conversation)
    prompt += "\nAI:"

    response = llm.invoke(prompt)

    print("\nAI:", response)
    print()

    ai_message = f"AI: {response}"

    conversation.append(ai_message)

    # Save AI response
    with open(MEMORY_FILE, "a", encoding="utf-8") as file:
        file.write(ai_message + "\n")