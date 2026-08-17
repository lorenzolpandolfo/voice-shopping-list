import os
from logging import getLogger
import locale
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


from groq import Groq

from src.constants.constants import (
    AGENT_CONTEXT,
    MASK_CURRENT_DATE,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE
)

load_dotenv()
logger = getLogger(__name__)
locale.setlocale(locale.LC_TIME, DEFAULT_LOCALE)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

JSON_AGENT =  os.environ.get("JSON_AGENT") or "openai/gpt-oss-20b"
WHISPER_AGENT = os.environ.get("WHISPER_AGENT") or "whisper-large-v3-turbo"


logger.info(JSON_AGENT, WHISPER_AGENT)

def groq_whisper(filename):
    logger.info(f"[Whisper Agent] Enviando o áudio para o agente {WHISPER_AGENT}...")
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model=WHISPER_AGENT,
            temperature=0,
            response_format="verbose_json",
            language="pt",
        )

    logger.info(
        f"[Whisper] Texto extraído do áudio: {transcription.text}",
    )
    return transcription.text


def groq_buy_data_to_json(content: str, msg_date):
    logger.info(
        f"[JSON Agent] Enviando ao agente {JSON_AGENT} a frase transcrita do áudio: {content}"
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": AGENT_CONTEXT.replace(
                    MASK_CURRENT_DATE,
                    f"{msg_date.astimezone(ZoneInfo(DEFAULT_TIMEZONE))}",
                )
                + content,
            }
        ],
        model=JSON_AGENT,
        temperature=0,
    )
    answer = chat_completion.choices[0].message.content
    logger.info(f"[JSON Agent] Resposta: {answer}")
    return answer
