import os
import json
import requests

def create_ollama_chatbot(system_prompt: str):
    OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Default Ollama server URL
    MODEL_NAME = "mistral"  # Or another model you have pulled (e.g., "mistral", "deepseek-coder")

    def chat(user_message: str):
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"
        
        # Collect streamed response
        reply_text = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "message" in data and "content" in data["message"]:
                    reply_text += data["message"]["content"]
        
        return reply_text.strip()

    return chat


if __name__ == "__main__":
    # Load knowledge base from JSON
    with open("blackcoffer.json", "r", encoding="utf-8") as f:
        company_data = json.load(f)

    # Combine all company data into a single knowledge base string
    knowledge_base = "\n".join(
        [f"{item['title']}: {item['text']} (Source: {item['url']})" for item in company_data]
    )

    SYSTEM_PROMPT = f"""
You are an AI receptionist for Blackcoffer. STRICTLY follow these instructions:

1. **ONLY answer using the numbered knowledge base provided below.**
2. NEVER make up information. If the answer is not in the knowledge base, respond exactly:
   "I'm sorry, I only provide information about Blackcoffer based on the knowledge base. I cannot answer that question."
3. Answer concisely, politely, and professionally.
4. For appointment bookings:
   - Ask for the user's full name, email, and phone number.
   - Confirm the details back to them.
   - Inform them that a confirmation email will be sent.

**Knowledge Base (Numbered Sections):**
{knowledge_base}

**RULES FOR RESPONSE:**
- Quote exact sentences from the numbered knowledge base whenever possible.
- Refer to section numbers when useful.
- Do NOT provide generic examples or unrelated explanations.
- Do NOT include personal opinions.
"""


    chatbot = create_ollama_chatbot(SYSTEM_PROMPT)

    while True:
        msg = input("\nYou: ")
        if msg.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        reply = chatbot(msg)
        print(f"Bot: {reply}")
