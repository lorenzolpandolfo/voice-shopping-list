import os

from dotenv import load_dotenv
from json import loads
from faster_whisper import WhisperModel
from anytype import create_anytype_object
from groq_service import groq_agent
import psutil

load_dotenv()

model = WhisperModel("small", device="cpu", compute_type="int8")


def transcribe_and_print(filename: str) -> str:
    segments, _ = model.transcribe(filename, language="pt")
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
        print("[AGENT ERROR] Erro ao chamar o agente: ", e)


def parse_json(json_data: str):
    try:
        return loads(json_data)

    except Exception as e:
        print("Erro ao parsear JSON: ", e)


def process_buy_audio_to_json_obj(filename: str):
    speech_to_text = transcribe_and_print(filename)
    json_data = buy_data_to_json(speech_to_text)
    return parse_json(json_data)


def find_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections(kind='tcp'):
                if str(conn.laddr.port) == str(port):
                    return proc

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def validate_anytype_server_is_running():
    if not find_process_on_port(os.getenv("ANYTYPE_PORT")):
        raise EnvironmentError("O processo do anytype não está rodando na porta definida no .env")

    else:
        print("[!] [ANYTYPE] Servidor local do Anytype rodando!")


if __name__ == "__main__":
    validate_anytype_server_is_running()

    obj_amazon = process_buy_audio_to_json_obj("fone_ouvido.ogg")
    create_anytype_object(obj_amazon)

