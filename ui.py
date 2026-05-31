import streamlit as st
from langchain_ollama import OllamaLLM
import time
from collections import deque

st.set_page_config(
    page_title="AI Trek Planner",
    page_icon="🥾"
)

st.title("🥾 AI Trek Planner")

@st.cache_resource
def load_model():
    return OllamaLLM(
        model="phi3",
        temperature=0.2,
        num_predict=180,
        keep_alive="30m",
    )

llm = load_model()

if "conversation" not in st.session_state:
    # Keep prompt size bounded so latency does not grow over time.
    st.session_state.conversation = deque(maxlen=12)

user_input = st.text_input(
    "Ask something about trekking",
    placeholder="Example: Suggest a beginner trek near Mumbai"
)

if st.button("Ask"):

    if user_input.strip():

        with st.spinner("AI is thinking..."):

            start = time.time()

            st.session_state.conversation.append(f"User: {user_input}")
            prompt = "\n".join(st.session_state.conversation) + "\nAI:"
            response = llm.invoke(prompt)
            st.session_state.conversation.append(f"AI: {response}")

            end = time.time()

        st.success(response)

        st.info(f"Response time: {end - start:.2f} seconds")