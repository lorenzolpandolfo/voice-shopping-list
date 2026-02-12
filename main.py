from core.services.audio_service import validate_anytype_server_is_running
from core.services.telegram_service import app

if __name__ == "__main__":
    validate_anytype_server_is_running()
    print("[!] 🤖 BOT iniciado e processando...")
    app.run_polling()

