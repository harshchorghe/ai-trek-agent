from langchain_ollama import OllamaLLM
from tools.location_extractor import extract_location

llm = OllamaLLM(
    model="phi3",
    temperature=0
)

while True:

    text = input("Message: ")

    print(
        "Location:",
        extract_location(text, llm)
    )