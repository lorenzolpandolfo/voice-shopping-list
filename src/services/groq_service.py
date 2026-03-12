import os
from datetime import datetime
from logging import getLogger

from dotenv import load_dotenv


from groq import Groq

from src.constants.constants import (
    AGENT_CONTEXT,
    MASK_CURRENT_DATE,
)

load_dotenv()
logger = getLogger(__name__)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

MODEL = "llama-3.1-8b-instant"
WHISPER_MODEL = "whisper-large-v3-turbo"


def groq_whisper(filename):
    logger.info("[Whisper] Enviando o áudio para o agente...")
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3-turbo",
            temperature=0,
            response_format="verbose_json",
        )

    logger.info(
        f"[Whisper] Texto extraído do áudio: {transcription.text}",
    )
    return transcription.text


def groq_buy_data_to_json(content: str):
    logger.info(
        f"[JSON Agent] Enviando ao agente {MODEL} a frase transcrita do áudio: {content}"
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": AGENT_CONTEXT.replace(
                    MASK_CURRENT_DATE, datetime.now().isoformat()
                )
                + content,
            }
        ],
        model=MODEL,
        temperature=0.1,
    )
    answer = chat_completion.choices[0].message.content
    logger.info(f"[JSON Agent] Resposta: {answer}")
    return answer
