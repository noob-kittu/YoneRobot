import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from Yone import (
    dispatcher, 
    ALLOW_EXCL, 
    StartTime,
    LOGGER)

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """ Hello{}, 
My name is {}, A telegram group management bot. I'm here to help you to manage your groups.
I have lots of handy features such as:
‣ Warning system
‣ Artificial intelligence
‣ Flood control system
‣ Note keeping system
‣ Filters keeping system
‣ Approvals and much more.

So what are you waiting for?
Add me in your groups and give me full rights to make me function well.
"""

buttons = [
    [
        InlineKeyboardButton(
            text="➕️ Add me to your chat ➕️", url="t.me/Yone_Robot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="News", callback_data="yone_"),
        InlineKeyboardButton(
            text="Support", url=f"https://t.me/{SUPPORT_CHAT}"
        ),
    ],
    [
        InlineKeyboardButton(text="Helps & Commands❔", callback_data="help_back"),
    ],
]


HELP_STRINGS = """
Hey there! My name is *{}*.
I'm a modular group management bot with a few fun extras! Have a look at the following for an idea of some of the things I can help you with. """.format(
    dispatcher.bot.first_name, ""
    if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n")



def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
            update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_text(
            "I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )




if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main()
