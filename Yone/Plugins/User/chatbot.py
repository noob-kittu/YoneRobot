import json
import re
import os
import html
import requests
import Yone.Database.chatbot_sql as sql
from korax import Kora

from time import sleep
from telegram.constants import ParseMode
from Yone import dispatcher, SUPPORT_CHAT, KORA_API_TOKEN
from Yone.Plugins.Admin.log_channel import gloggable
from telegram import (CallbackQuery, Chat, MessageEntity, InlineKeyboardButton, 
                      InlineKeyboardMarkup, Message, Update, Bot, User)

from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          ApplicationHandlerStop, filters, MessageHandler, 
                          )

from telegram.error import BadRequest, RetryAfter, Forbidden
from telegram.constants import ParseMode

from Yone.Handlers.filters import CustomFilters
from Yone.Handlers.validation import user_admin, user_admin_no_reply

from telegram.helpers import mention_html, mention_markdown, escape_markdown

kora = Kora(KORA_API_TOKEN)
owner = "kittu"
botname = "kora"
 
@user_admin_no_reply
@gloggable
async def yonerm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_yone = sql.rem_yone(chat.id)
        if is_yone:
            is_yone = sql.rem_yone(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_DISABLED\n"
                f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            update.effective_message.edit_text(
                "Chatbot disable by {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )

    return ""

@user_admin_no_reply
@gloggable
async def yoneadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"add_chat\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        is_yone = sql.set_yone(chat.id)
        if is_yone:
            is_yone = sql.set_yone(user_id)
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
async def yone(update: Update, context: CallbackContext):
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
    await message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

async def yone_message(context: CallbackContext, message):
    reply_message = await message.reply_to_message
    if message.text.lower() == "yone":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False
        

async def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_yone = sql.is_yone(chat_id)
    if not is_yone:
        return
	
    if message.text and not message.document:
        if not yone_message(context, message):
            return
        Message = message.text
        bot.send_chat_action(chat_id, action="typing")
        yone = kora.chatbot(message,owner,botname)
        sleep(0.3)
        await message.reply_text(yone, timeout=60)

async def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_yone_chats()
    text = "<b>YONE-Enabled Chats</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Forbidden):
            sql.rem_yone(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    await update.effective_message.reply_text(text, parse_mode="HTML")

__help__ = """We have highly artificial intelligence chatbot of telegram which provides you real and attractive experience of chatting.
*Admins only Commands*:
  ‣ `/Chatbot`*:* Shows chatbot control panel
  """

__mod_name__ = "Chatbot"


CHATBOTK_HANDLER = CommandHandler("ChatBot", yone )
ADD_CHAT_HANDLER = CallbackQueryHandler(yoneadd, pattern=r"add_chat" )
RM_CHAT_HANDLER = CallbackQueryHandler(yonerm, pattern=r"rm_chat" )
CHATBOT_HANDLER = MessageHandler(
    filters.TEXT & (filters.Regex(r"^#[^\s]+") & filters.Regex(r"^!")
                    & filters.Regex(r"^\/")), chatbot )
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter )

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_HANDLER,
]
