#  COPYRIGHT (C) 2021 @NoobKittu
import time, psutil
from Yone import SUPPORT_CHAT
from platform import python_version
from Yone import StartTime, dispatcher
from Yone.Plugins.disable import DisableAbleCommandHandler
from telegram import Update, ParseMode,  InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, run_async
from telegram.utils.helpers import mention_html
from Yone.__main__ import get_readable_time


PHOTO = "https://telegra.ph/file/b749b0e80e82291e85e10.jpg"

 
def alive(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    user_id = user.id
    args = message.text.split(" ", 1)
    uptime = get_readable_time((time.time() - StartTime))



    text = (
        f"Hello {mention_html(user.id, user.first_name)}, I'm {bot.first_name}\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━\n"
        f"┣[• Owner : @{user.username}  \n"
        f"┣[• Uptime : {uptime} \n"
        f"┣[• Core : {psutil.cpu_percent()}%\n"
        f"┣[• Python   : Ver {python_version()} \n"
        f"┗━━━━━━━━━━━━━━━━━━━")
 

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="SUPPORT", 
                url=f"https://t.me/{SUPPORT_CHAT}"),
            InlineKeyboardButton(
                text="DEVLOPER", 
                url=f"https://t.me/{user.username}")
            
        ],
        
        ])
    message.reply_photo(
                PHOTO,
                caption=(text),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                
            )


ALIVE_HANDLER = DisableAbleCommandHandler("alive", alive, run_async=True)
dispatcher.add_handler(ALIVE_HANDLER)