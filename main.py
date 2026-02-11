from dotenv import load_dotenv
from json import loads
from datetime import datetime

from faster_whisper import WhisperModel

from google import genai
from google.genai import types

from anytype import create_anytype_object

load_dotenv()

GEMINI_CONTEXT = f"""
Você vai receber dados de compras, como:
- uma breve descrição da compra
- valor
- data da compra (se não especificado, considere o dia atual: {datetime.now().isoformat()})

Você deve coletar estes dados e retornar em estilo JSON, conforme o modelo:
{{
  "name": "Caneca" (avalie conforme a descrição o nome do item comprado),
  "description": "Compra de caneca na Amazon",
  "price": 10,
  "date": "YYYY-MM-DDTHH:MM:SSZ"
}}

Você deve retornar APENAS o conteúdo do JSON, sem codeblock!
Você pode melhorar a descrição para ficar mais legível
Caso especificado uma data de compra relativa, por exemplo "ontem" ou "semana passada", você deve considerar em relação ao dia atual especificado.
"""

model = WhisperModel("small", device="cpu", compute_type="int8")
client = genai.Client()

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
FALLBACK_GEMINI_MODEL = "gemini-2.0-flash"

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
        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_CONTEXT),
            contents=buy_speech_to_text_data
        )

    except Exception:
        print("[WARN] Usando modelo fallback do Gemini")
        response = client.models.generate_content(
            model=FALLBACK_GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_CONTEXT),
            contents=buy_speech_to_text_data
        )

    response = response.text
    return response


def parse_json(json_data: str):
    try:
        return loads(json_data)

    except Exception as e:
        print("Erro ao parsear JSON: ", e)


def process_buy_audio_to_json_obj(filename: str):
    speech_to_text = transcribe_and_print(filename)
    json_data = buy_data_to_json(speech_to_text)
    return parse_json(json_data)

# Exemplos

obj_amazon = process_buy_audio_to_json_obj("compra amazon.ogg")
create_anytype_object(obj_amazon)

obj_ml = process_buy_audio_to_json_obj("compra mercadolivre.ogg")
create_anytype_object(obj_ml)


