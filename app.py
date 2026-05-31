from langchain_ollama import OllamaLLM

llm = OllamaLLM(
	model="phi3",
	temperature=0.2,
	num_predict=180,
	keep_alive="30m",
)

response = llm.invoke("Suggest a beginner-friendly trek in Maharashtra")

print(response)