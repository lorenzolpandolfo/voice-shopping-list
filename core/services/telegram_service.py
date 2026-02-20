from datetime import datetime
import os
import random

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from core.exceptions.anytype_exception import AnytypeException
from core.exceptions.groq_exception import GroqException
from core.services.anytype_service import create_anytype_object
from core.services.audio_service import transcribe, buy_data_to_json, \
    parse_json
from core.services.google_service import save_data_to_spreadsheet
from core.utils import is_integration_strategy_anytype, is_integration_strategy_spreadsheets, \
    get_formatted_integration_strategy

load_dotenv()

TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
TELEGRAM_MY_USER_ID = os.getenv("TELEGRAM_MY_USER_ID")

GREETINGS = ["Olá", "Salve", "Boa pai", "Fala padrinho", "Fala meu velho", "Daí, meu"]
EMOIJS = ["😎", "😉", "🤑"]
FUNNY_INTERACTIONS = ["Vamo segurar esses gastos aí hein 😅", "Assim não dá pra juntar grana pai 💸", "Tá cheio da grana em 💸💰"]


async def receive_and_process_audio_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.voice:
        file_id = update.message.voice.file_id
        ext = "ogg"
    elif update.message.audio:
        file_id = update.message.audio.file_id
        ext = "mp3"
    else:
        return

    file = await context.bot.get_file(file_id)
    audio_file_path = os.path.join(os.getcwd(), f"audios/{file_id}.{ext}")

    print(f"[TELEGRAM] Salvando audio em {audio_file_path}")
    await file.download_to_drive(audio_file_path)

    try:
        saved_json_obj: dict = process_audio_file(audio_file_path)
        success_answer = create_user_answer_text(saved_json_obj)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=success_answer, parse_mode="HTML")

    except AnytypeException as e:
        os.remove(audio_file_path)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"😢 Desculpe, houve um erro com o Anytype:\n{e}", parse_mode="HTML")

    except GroqException as e:
        os.remove(audio_file_path)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"😢 Desculpe, houve um erro com o Groq:\n{e}", parse_mode="HTML")

    except Exception as e:
        os.remove(audio_file_path)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"😢 Desculpe, houve um erro: {e}", parse_mode="HTML")


def process_audio_file(audio_file_path: str) -> dict:
    print(f"[AUDIO] Processando audio...")
    speech_to_text = transcribe(audio_file_path)
    raw_json_data = buy_data_to_json(speech_to_text)
    payload = parse_json(raw_json_data)

    process_data_integration(payload)

    print(f"[AUDIO] Apagando arquivo de áudio: {audio_file_path}")
    os.remove(audio_file_path)

    return payload

def process_data_integration(payload):
    """Integrates to Anytype or Google Spreadsheets as configured in .env"""

    if is_integration_strategy_anytype():
        print(f"[ANYTYPE] Salvando objeto JSON no Anytype...\n > {payload}\n")
        create_anytype_object(payload)
        return

    elif is_integration_strategy_spreadsheets():
        print(f"[GOOGLE SPREADSHEETS] Salvando registro na tabela do Google Planilhas...\n > {payload}\n")
        save_data_to_spreadsheet(payload)
        return

    else:
        raise EnvironmentError("Invalid INTEGRATION_STRATEGY. Value must be anytype or spreadsheets. You can set it in the .env file.")


def create_user_answer_text(saved_json_obj: dict) -> str:
    funny_interaction = random.randint(0, 3) == 0
    funny_interaction = random.choice(FUNNY_INTERACTIONS) + "\n" if funny_interaction else ""

    greeting = random.choice(GREETINGS)
    emoji = random.choice(EMOIJS)

    buy_name = saved_json_obj.get('name')
    buy_category = saved_json_obj.get('category')
    buy_price = saved_json_obj.get('price')
    buy_date = datetime.fromisoformat(saved_json_obj.get('date').replace("Z", "+00:00")).strftime("%d de %B de %Y às %H:%M")

    buy_data = f"""
<b>{buy_name}</b>
<b>Valor</b>: {buy_price} reais
<b>Data</b>: {buy_date}
<b>Categoria</b>: {buy_category}
"""

    return f"""
{greeting}! {emoji}

Anotei o teu gasto no <b>{get_formatted_integration_strategy()}</b>. Segue os dados:
{buy_data}
{funny_interaction}Até a próxima!
"""

app = ApplicationBuilder().token(TELEGRAM_BOT_API_KEY).build()
filter_user_id = filters.User(user_id=TELEGRAM_BOT_API_KEY)

audio_handler = MessageHandler(filter_user_id | filters.VOICE | filters.AUDIO, receive_and_process_audio_file)
app.add_handler(audio_handler)
