import os
from dotenv import load_dotenv

load_dotenv()

INTEGRATION_STRATEGY = os.getenv("INTEGRATION_STRATEGY").lower()

if not INTEGRATION_STRATEGY:
    raise EnvironmentError("Environment variable INTEGRATION_STRATEGY is not defined. Must be 'anytype' or 'spreadsheets'.")

def is_integration_strategy_spreadsheets():
    return INTEGRATION_STRATEGY.lower() == "spreadsheets"

def is_integration_strategy_anytype():
    return INTEGRATION_STRATEGY.lower() == "anytype"

def get_formatted_integration_strategy():

    if is_integration_strategy_anytype():
        return "Anytype"

    else:
        return "Google Planilhas"


def is_groq_whisper():
    return not os.getenv("WHISPER_MODEL")