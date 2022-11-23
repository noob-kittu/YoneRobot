import re, html
from telegram import ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    run_async,
)
from telegram.utils.helpers import mention_html, mention_markdown, escape_markdown
from Yone.Handlers.validation import user_admin, user_admin_no_reply
from Yone.Plugins.Admin.log_channel import gloggable




@user_admin_no_reply
@gloggable
def anti_c_mode_off(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_mode\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_channel = sql.rem_channel(chat.id)
        if is_channel:
            is_channel = sql.rem_channel(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ANTI_CHANNEL_MODE_DISABLED\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Anti Channel Mode disable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""



@user_admin_no_reply
@gloggable
def anti_c_mode_on(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_channel\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_channel = sql.set_yone(chat.id)
        if is_channel:
            is_channel = sql.set_yone(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_ENABLE\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot enable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""

@user_admin
@gloggable
def yone(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message
    msg = f"Choose an option"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            text="Enable",
            callback_data="add_chat({})")],
       [
        InlineKeyboardButton(
            text="Disable",
            callback_data="rm_chat({})")]])
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
