import os
import psutil

from dotenv import load_dotenv
from json import loads
from faster_whisper import WhisperModel

from core.exceptions.groq_exception import GroqException
from core.services.groq_service import groq_agent

load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL")


def transcribe(filename: str) -> str:
    segments, _ = whisper_model.transcribe(filename, language="pt")
    full_text = ""

    print("\n[!] Texto da fala: ")
    for s in segments:
        print(s.text, end="")
        full_text += s.text

    print()
    return full_text


def buy_data_to_json(buy_speech_to_text_data: str):
    try:
        return groq_agent(buy_speech_to_text_data)

    except Exception as e:
        raise GroqException("[AGENT ERROR] Erro ao chamar o agente: ", e)


def parse_json(json_data: str):
    try:
        return loads(json_data)

    except Exception as e:
        print("[JSON ERROR] Erro ao parsear JSON: ", e)


def has_process_running_on_port(port: int) -> bool:
    for c in psutil.net_connections(kind="inet"):
        if c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN:
            return True
    return False

def validate_anytype_server_is_running():
    anytype_port = int(os.getenv("ANYTYPE_PORT"))

    if not has_process_running_on_port(anytype_port):
        raise EnvironmentError(f"[ANYTYPE ERROR] O processo do Anytype não está rodando na porta {anytype_port}, definida no .env")

    else:
        print("[ANYTYPE] Anytype está rodando na porta ", anytype_port)


whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

