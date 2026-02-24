import os
import random
from datetime import datetime
from json import loads
from logging import getLogger


from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from src.services.google_service import save_data_to_spreadsheet
from src.services.groq_service import groq_buy_data_to_json, groq_whisper
from src.services.user_data_service import get_user_data_by_id

load_dotenv()
logger = getLogger(__name__)
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")

GREETINGS = ["Olá", "Salve", "Boa pai", "Fala padrinho", "Fala meu velho", "Daí, meu"]
EMOIJS = ["😎", "😉", "🤑"]
FUNNY_INTERACTIONS = [
    "Vamo segurar esses gastos aí hein 😅",
    "Assim não dá pra juntar grana pai 💸",
    "Tá cheio da grana em 💸💰",
]


async def receive_and_process_audio_file(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if update.message.voice:
        file_id = update.message.voice.file_id
        ext = "ogg"
    elif update.message.audio:
        file_id = update.message.audio.file_id
        ext = "mp3"
    else:
        return

    user_id = str(update.effective_user.id)
    user_config = get_user_data_by_id(user_id)

    if not user_config:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="😢 Foi mal, mas eu não tô configurado pra te responder",
        )
        return

    file = await context.bot.get_file(file_id)
    audio_file_path = os.path.join(os.getcwd(), f"audios/{file_id}.{ext}")

    logger.info(f"[Telegram] Salvando áudio em {audio_file_path}")
    await file.download_to_drive(audio_file_path)

    try:
        saved_json_obj: dict = process_audio_file(audio_file_path, user_id, user_config)
        success_answer = create_user_answer_text(saved_json_obj)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=success_answer, parse_mode="HTML"
        )

    except Exception as e:
        os.remove(audio_file_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"😢 Desculpe, houve um erro: {e}",
            parse_mode="HTML",
        )


def process_audio_file(audio_file_path: str, user_id: str, user_config: dict) -> dict:
    logger.info("[Audio] Processando áudio...")
    speech_to_text = groq_whisper(audio_file_path)

    raw_json_data = groq_buy_data_to_json(speech_to_text)
    payload = loads(raw_json_data)

    logger.info("[Spreadsheets] Salvando registro na tabela do Google Planilhas...")
    save_data_to_spreadsheet(payload, user_id, user_config)

    logger.info(f"[Audio] Apagando arquivo de áudio: {audio_file_path}")
    os.remove(audio_file_path)

    return payload


def create_user_answer_text(saved_json_obj: dict) -> str:
    funny_interaction = random.randint(0, 3) == 0
    funny_interaction = (
        random.choice(FUNNY_INTERACTIONS) + "\n" if funny_interaction else ""
    )

    greeting = random.choice(GREETINGS)
    emoji = random.choice(EMOIJS)

    buy_name = saved_json_obj.get("name")
    buy_category = saved_json_obj.get("category")
    buy_price = saved_json_obj.get("price")
    buy_date = datetime.fromisoformat(
        saved_json_obj.get("date").replace("Z", "+00:00")
    ).strftime("%d de %B de %Y às %H:%M")

    buy_data = f"""
<b>{buy_name}</b>
<b>Valor</b>: {buy_price} reais
<b>Data</b>: {buy_date}
<b>Categoria</b>: {buy_category}
"""

    return f"""
{greeting}! {emoji}

Anotei o teu gasto no <b>Google Planilhas</b>. Segue os dados:
{buy_data}
{funny_interaction}Até a próxima!
"""


app = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()

audio_handler = MessageHandler(
    filters.VOICE | filters.AUDIO, receive_and_process_audio_file
)
app.add_handler(audio_handler)
