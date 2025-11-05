import streamlit as st
from supabase import create_client, Client
import ollama

# ---------- Page Setup ----------
st.set_page_config(page_title="AI Receptionist", page_icon="🤖")
st.title("🤖 AI Receptionist - Blackcoffer")

# ---------- Supabase Connection ----------
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# ---------- Generate Response ----------
def generate_response(query):
    try:
        embedding = ollama.embeddings(model="nomic-embed-text", prompt=query)["embedding"]

        response = supabase.rpc(
            "match_vectors",
            {"query_embedding": embedding, "match_threshold": 0.8, "match_count": 3}
        ).execute()

        if not response.data:
            return "Sorry, I couldn’t find related information."

        context = " ".join([r["content"] for r in response.data])

        completion = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are an AI receptionist for Blackcoffer."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ])
        return completion['message']['content']
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
