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
    get_user_credentials_google,
)

load_dotenv()
logger = getLogger(__name__)
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")

REPO_URL = "https://github.com/lorenzolpandolfo/voice-shopping-list"
GREETINGS = ["Olá", "Salve", "Boa pai", "Fala padrinho", "Fala meu velho", "Daí, meu"]
EMOIJS = ["😎", "😉", "🤑"]
FUNNY_INTERACTIONS = [
    "Vamo segurar esses gastos aí hein 😅",
    "Assim não dá pra juntar grana pai 💸",
    "Tá cheio da grana em 💸💰",
]


async def _validate_has_google_credentials(context, update) -> bool:

    user_id = str(update.effective_user.id)
    credentials = get_user_credentials_google(user_id)

    if credentials:
        return True

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Você precisa se autenticar para que eu consiga acessar sua planilha do Google.\n"
            "Utilize o comando <code>/auth</code> e siga as etapas."
        ),
        parse_mode="HTML",
    )
    return False


async def _validate_user_data(context, update) -> dict | None:
    user_id = str(update.effective_user.id)
    data = get_user_data_by_id(user_id)

    if data:
        return data

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="😢 Foi mal, mas eu não tô configurado pra te responder",
    )
    return None


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
    user_config = await _validate_user_data(context, update)
    if not user_config:
        return

    if not await _validate_has_google_credentials(context, update):
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

    if not await _validate_user_data(context, update):
        return

    user_code, verification_url = start_device_auth(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Para autorizar o acesso na sua <b>Google Planilha</b>, copie o código abaixo:\n"
            f"\n<code>{user_code}</code>\n\n"
            f"E acesse o link:\n{verification_url}\n\n"
            f"Ao finalizar, envie <b>pronto</b> para eu concluir a sua autenticação."
        ),
        parse_mode="HTML",
    )


async def finish_auth_on_message(update, context):
    if not await _validate_user_data(context, update):
        return

    text_message: str = update.message.text

    if text_message.lower().strip() != "pronto":
        return

    user_id = str(update.effective_user.id)
    try:
        credentials = finish_device_auth(user_id)

        if credentials is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Não encontrei a sua solicitação de autenticação.",
            )
            return

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🎉 Autorização concluída! Agora posso acessar sua planilha.",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"⚠️ Ainda não autorizado ou erro: {e}",
        )


async def start_command(update, context):

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"🤖✌ Olá, eu sou o Balance Bot! O robô de <a href='{REPO_URL}'>código aberto</a> feito para organizar a sua vida financeira. 🤑\n\n"
            f"Eu recebo áudios de compras, transcrevo-os para texto e organizo na sua Google Planilhas.\n\n"
            f"É muito simples! Experimente dizer: <i>Comprei morango por 10 reais hoje.</i>\n\n"
            f"Vou anotar o <b>título</b> da sua compra, uma <b>descrição</b>, o <b>preço</b>, <b>categoria</b> e <b>data da compra</b>.\n\nPode deixar comigo! 😎"
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    user_id = str(update.effective_user.id)
    user_data = get_user_data_by_id(user_id)
    credentials = get_user_credentials_google(user_id)

    if not user_data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Verifiquei que você não é um usuário registrado.\n\n"
                "Entre em contato com o meu mantenedor para liberar o seu acesso."
            ),
            parse_mode="HTML",
        )
        return

    if not credentials:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Verifiquei que você já é um usuário registrado, que top! 🥳\n\n"
                "Mas não encontrei a sua autenticação com o Google Planilhas.\n\n"
                "Para realizar, envie <code>/auth</code>."
            ),
            parse_mode="HTML",
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Verifiquei que você já é um usuário registrado, que top! 🥳\n\n"
            "E também encontrei a sua autenticação com o Google Planilhas!\n\n"
            "Você já está liberado para enviar áudios."
        ),
        parse_mode="HTML",
    )


app = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()

app.add_handler(
    MessageHandler(filters.VOICE | filters.AUDIO, receive_and_process_audio_file)
)
app.add_handler(CommandHandler("auth", auth_command))
app.add_handler(CommandHandler("start", start_command))
app.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), finish_auth_on_message)
)
