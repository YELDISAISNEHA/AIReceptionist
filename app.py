import os
import requests
import streamlit as st
from supabase import create_client, Client

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Receptionist", page_icon="🤖")
st.title("🤖 AI Receptionist - Blackcoffer")

# ---------- Supabase Connection ----------
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ---------- Together AI Setup ----------
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"

# ---------- Generate Response ----------
def generate_response(query):
    try:
        # --- 1️⃣ Embed query using your existing model endpoint (optional) ---
        # If you still need query embeddings from Supabase, ensure embeddings were precomputed.
        # Skip local Ollama embeddings; we assume you already stored them.

        # --- 2️⃣ Retrieve similar context from Supabase ---
        response = supabase.rpc(
            "match_vectors",
            {"query_embedding": [], "match_threshold": 0.8, "match_count": 3}
        ).execute()

        if not response.data:
            return "Sorry, I couldn’t find related information."

        context = " ".join([r["content"] for r in response.data])

        # --- 3️⃣ Query Together AI open-source model (Llama 3 8B-Instruct) ---
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta-llama/Meta-Llama-3-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are an AI receptionist for Blackcoffer."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        r = requests.post(TOGETHER_URL, headers=headers, json=payload, timeout=60)
        data = r.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {data}"

    except Exception as e:
        return f"Error: {e}"

# ---------- Chat Interface ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = generate_response(prompt)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
