import os
import random
from datetime import datetime
from json import loads
from logging import getLogger


from dotenv import load_dotenv
from google.auth.exceptions import RefreshError
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.services.google_service import save_data_to_spreadsheet
from src.services.groq_service import groq_buy_data_to_json, groq_whisper
from src.services.user_data_service import get_user_data_by_id
from src.services.google_oauth_service import (
    start_device_auth,
    finish_device_auth,
    get_user_credentials,
)

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


async def _validate_can_process_audio(
    context, update, user_config, credentials
) -> bool:

    if not user_config:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="😢 Foi mal, mas eu não tô configurado pra te responder",
        )
        return False

    if not credentials:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Você precisa se autorizar para que eu consiga acessar sua planilha do Google.\n"
                "Utilize o comando <code>/auth</code> e siga as etapas."
            ),
            parse_mode="HTML",
        )
        return False

    return True


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
    credentials = get_user_credentials(user_id)

    if not await _validate_can_process_audio(context, update, user_config, credentials):
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

    except RefreshError:
        os.remove(audio_file_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="A sua autenticação foi revogada ou expirada. Autentique-se com <code>/auth</code> e tente novamente.",
            parse_mode="HTML",
        )

    except Exception as e:
        os.remove(audio_file_path)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"😢 Desculpe, houve um erro: {e}",
            parse_mode="HTML",
        )


def process_audio_file(audio_file_path: str, user_id: str, user_config: dict) -> dict:
    """
    Envia o áudio para o Whisper, depois para o agente que cria o JSON, salva no Google Planilhas e apaga o arquivo do áudio.
    Retorna o payload salvo.
    """

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
    greeting = random.choice(GREETINGS)
    emoji = random.choice(EMOIJS)

    funny_interaction = ""
    if random.randint(0, 4) == 0:
        funny_interaction = random.choice(FUNNY_INTERACTIONS) + "\n"

    buy_name = saved_json_obj.get("name")
    buy_category = saved_json_obj.get("category")
    buy_price = saved_json_obj.get("price")
    raw_date = saved_json_obj.get("date").replace("Z", "+00:00")
    buy_date = datetime.fromisoformat(raw_date).strftime("%d de %B de %Y às %H:%M")

    buy_data = (
        f"<b>{buy_name}</b>\n"
        f"<b>Valor</b>: {buy_price} reais\n"
        f"<b>Data</b>: {buy_date}\n"
        f"<b>Categoria</b>: {buy_category}\n"
    )

    return (
        f"{greeting}! {emoji}\n\n"
        f"Anotei o teu gasto no <b>Google Planilhas</b>. Segue os dados:\n\n"
        f"{buy_data}"
        f"\n{funny_interaction}Até a próxima!"
    )


async def auth_command(update, context):
    user_id = str(update.effective_user.id)
    user_code, verification_url = start_device_auth(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Para autorizar o acesso na sua planilha do Google, acesse:\n{verification_url}\n\n"
            f"E digite o código: <code>{user_code}</code>\n\n"
            f"Depois, envie <b>pronto</b> para eu finalizar a sua autenticação."
        ),
        parse_mode="HTML",
    )


async def finish_auth_on_message(update, context):
    text_message: str = update.message.text

    if text_message.lower().strip() != "pronto":
        return

    user_id = str(update.effective_user.id)
    try:
        finish_device_auth(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🎉 Autorização concluída! Agora posso acessar sua planilha.",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Ainda não autorizado ou erro: {e}",
        )


app = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()

app.add_handler(
    MessageHandler(filters.VOICE | filters.AUDIO, receive_and_process_audio_file)
)
app.add_handler(CommandHandler("auth", auth_command))
app.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), finish_auth_on_message)
)
