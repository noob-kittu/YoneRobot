import logging, os, sys, time
import telegram.ext as tg
from telethon.sessions import MemorySession
from telethon import TelegramClient


StartTime = time.time()


# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)


# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error(
        "You must have a python version of at least 3.6! Multiple features depend on this. Bot quitting."
    )
    quit(1)

ENV = bool(os.environ.get("ENV", False))

if ENV:
    TOKEN = os.environ.get("TOKEN", None)

    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", None))
    except ValueError:
        raise Exception("Your OWNER_ID env variable is not a valid integer.")
    try:
        INSPECTOR = set(int(x) for x in os.environ.get("INSPECTOR", "").split())
        DEV_USERS = set(int(x) for x in os.environ.get("DEV_USERS", "").split())
    except ValueError:
        raise Exception("Your inspector(sudo) or dev users list does not contain valid integers.")

    try:
        REQUESTER = set(int(x) for x in os.environ.get("REQUESTER", "").split())
    except ValueError:
        raise Exception("Your requester list does not contain valid integers.")
    try:
        API_ID = int(os.environ.get("API_ID", None))
    except ValueError:
        raise Exception("Your API_ID env variable is not a valid integer.")

    try:
        HASH_API = os.environ.get("HASH_API", None)
    except ValueError:
        raise Exception("Please Add Hash Api key to start the bot")

    DB_URI = os.environ.get("DATABASE_URL")
    WORKERS = int(os.environ.get("WORKERS", 8))
    ALLOW_EXCL = os.environ.get('ALLOW_EXCL', False)
    SUPPORT_CHAT = int(os.environ.get("SUPPORT_CHAT", None))

    WEBHOOK = bool(os.environ.get("WEBHOOK", False))
    CERT_PATH = os.environ.get("CERT_PATH")
    URL = os.environ.get("URL", "")  # Does not contain token
    PORT = int(os.environ.get("PORT", 5000))




else:
    from Yone.config import Development as Config

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")
# telegram bot requered things from telegram org 
    API_ID = Config.API_ID
    API_HASH = Config.API_HASH
    TOKEN = Config.TOKEN
    DB_URI = Config.SQLALCHEMY_DATABASE_URI

    SUPPORT_CHAT = Config.SUPPORT_CHAT

# WEBHOOK REQUERED THINGS
    WORKERS = Config.WORKERS
    ALLOW_EXCL = Config.ALLOW_EXCL
    WEBHOOK = Config.WEBHOOK
    CERT_PATH = Config.CERT_PATH
    PORT = Config.PORT
    URL = Config.URL


updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
dispatcher = updater.dispatcher



