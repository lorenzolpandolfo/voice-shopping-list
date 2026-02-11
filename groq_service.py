import os

from ai_context import AGENT_CONTEXT
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

MODEL = "allam-2-7b"

def groq_agent(content: str):
    print("Acessando agente do GROQ")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": AGENT_CONTEXT + content,
            }
        ],
        model=MODEL,
    )
    print("Resposta do agente: ", chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content