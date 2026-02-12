import os

from dotenv import load_dotenv
from groq import Groq
from core.constants.ai_context import AGENT_CONTEXT

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

MODEL = "llama-3.1-8b-instant"

def groq_agent(content: str):
    print(f"[GROQ] Enviando ao agente {MODEL}: ", content)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": AGENT_CONTEXT + content,
            }
        ],
        model=MODEL,
        temperature=0.1
    )
    print("[GROQ] Resposta do agente: ", chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content