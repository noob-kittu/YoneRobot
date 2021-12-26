import logging, os, sys, time
import telegram.ext as tg


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
        API_ID = int(os.environ.get("API_ID", None))
    except ValueError:
        raise Exception("Your API_ID env variable is not a valid integer.")

    try:
        HASH_API = os.environ.get("HASH_API", None)
    except ValueError:
        raise Exception("Please Add Hash Api key to start the bot")

    DB_URI = os.environ.get("DATABASE_URL")
    WORKERS = int(os.environ.get("WORKERS", 8))



else:
    from Yone.config import Development as Config

    TOKEN = Config.TOKEN

    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Your OWNER_ID variable is not a valid integer.")

    API_ID = Config.API_ID
    API_HASH = Config.API_HASH
    DB_URI = Config.SQLALCHEMY_DATABASE_URI
    WORKERS = Config.WORKERS


updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
dispatcher = updater.dispatcher



     