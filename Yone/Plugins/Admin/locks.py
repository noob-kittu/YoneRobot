import html

from telegram import Message, Chat, ParseMode, MessageEntity
from telegram import TelegramError, ChatPermissions
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from alphabet_detector import AlphabetDetector

import Yone.Database.locks_sql as sql
from Yone import dispatcher, INSPECTOR, LOGGER
from Yone.Plugins.disable import DisableAbleCommandHandler
from Yone.Handlers.validation import (
    can_delete,
    is_user_admin,
    user_not_admin,
    is_bot_admin,
    user_admin,
)
from Yone.Plugins.Admin.log_channel import loggable
from Yone.Plugins.Admin.connection import connected
from Yone.Database.approve_sql import is_approved
from Yone.Handlers.alternate import send_message, typing_action

ad = AlphabetDetector()

LOCK_TYPES = {
    "audio": Filters.audio,
    "voice": Filters.voice,
    "document": Filters.document & ~Filters.animation,
    "video": Filters.video,
    "contact": Filters.contact,
    "photo": Filters.photo,
    "url": Filters.entity(MessageEntity.URL)
    | Filters.caption_entity(MessageEntity.URL),
    "bots": Filters.status_update.new_chat_members,
    "forward": Filters.forwarded,
    "game": Filters.game,
    "location": Filters.location,
    "egame": Filters.dice,
    "rtl": "rtl",
    "button": "button",
    "inline": "inline",
}

LOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": False,
        "can_send_media_messages": False,
        "can_send_polls": False,
        "can_send_other_messages": False,
        "can_add_web_page_previews": False,
        "can_change_info": False,
        "can_invite_users": False,
        "can_pin_messages": False,
    },
    "messages": {"can_send_messages": False},
    "media": {"can_send_media_messages": False},
    "sticker": {"can_send_other_messages": False},
    "gif": {"can_send_other_messages": False},
    "poll": {"can_send_polls": False},
    "other": {"can_send_other_messages": False},
    "previews": {"can_add_web_page_previews": False},
    "info": {"can_change_info": False},
    "invite": {"can_invite_users": False},
    "pin": {"can_pin_messages": False},
}

UNLOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": True,
        "can_send_media_messages": True,
        "can_send_polls": True,
        "can_send_other_messages": True,
        "can_add_web_page_previews": True,
        "can_invite_users": True,
    },
    "messages": {"can_send_messages": True},
    "media": {"can_send_media_messages": True},
    "sticker": {"can_send_other_messages": True},
    "gif": {"can_send_other_messages": True},
    "poll": {"can_send_polls": True},
    "other": {"can_send_other_messages": True},
    "previews": {"can_add_web_page_previews": True},
    "info": {"can_change_info": True},
    "invite": {"can_invite_users": True},
    "pin": {"can_pin_messages": True},
}

PERM_GROUP = 1
REST_GROUP = 2

def alltypes():
    lall = []
    for i in LOCK_TYPES:
        lall.append(i)
    for i in LOCK_CHAT_RESTRICTION:
        lall.append(i)
    return lall

# NOT ASYNC
def restr_members(
    bot, chat_id, members, messages=False, media=False, other=False, previews=False,
):
    for mem in members:
        if mem.user in INSPECTOR:
            pass
        try:
            bot.restrict_chat_member(
                chat_id,
                mem.user,
                can_send_messages=messages,
                can_send_media_messages=media,
                can_send_other_messages=other,
                can_add_web_page_previews=previews,
            )
        except TelegramError:
            pass


# NOT ASYNC
def unrestr_members(
    bot, chat_id, members, messages=True, media=True, other=True, previews=True,
):
    for mem in members:
        try:
            bot.restrict_chat_member(
                chat_id,
                mem.user,
                can_send_messages=messages,
                can_send_media_messages=media,
                can_send_other_messages=other,
                can_add_web_page_previews=previews,
            )
        except TelegramError:
            pass



def locktypes(update, context):
    update.effective_message.reply_text(
        "\n • ".join(
            ["Locks available: "]
            + sorted(list(LOCK_TYPES) + list(LOCK_CHAT_RESTRICTION)),
        ),
    )



@user_admin
@loggable
@typing_action
def lock(update, context) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if (
        can_delete(chat, context.bot.id)
        or update.effective_message.chat.type == "private"
    ):
        if len(args) >= 1:

            #Support for lockname(s)
            memdata = alltypes()

            if args[0].lower().endswith('s') and not args[0].lower() in memdata:
                ltype = args[0].lower()[:-1]
            elif not args[0].lower().endswith('s') and args[0].lower() + 's' in memdata:
                ltype = args[0].lower() + 's'
            else:
                ltype = args[0].lower()

            if ltype in LOCK_TYPES:
                # Connection check
                conn = connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat = dispatcher.bot.getChat(conn)
                    chat_id = conn
                    chat_name = chat.title
                    text = f"Locked {ltype} for non-admins in {chat_name}!"
                else:
                    if update.effective_message.chat.type == "private":
                        send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat = update.effective_chat
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = f"Locked {ltype} for non-admins!"
                sql.update_lock(chat.id, ltype, locked=True)
                send_message(update.effective_message, text, parse_mode="markdown")

                return (
                    "<b>{}:</b>"
                    "\n#LOCK"
                    "\n<b>Admin:</b> {}"
                    "\nLocked <code>{}</code>.".format(
                        html.escape(chat.title),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            elif ltype in LOCK_CHAT_RESTRICTION:
                # Connection check
                conn = connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat = dispatcher.bot.getChat(conn)
                    chat_id = conn
                    chat_name = chat.title
                    text = "Locked {} for all non-admins in {}!".format(
                        ltype, chat_name,
                    )
                else:
                    if update.effective_message.chat.type == "private":
                        send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat = update.effective_chat
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = f"Locked {ltype} for all non-admins!"

                current_permission = context.bot.getChat(chat_id).permissions
                context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=get_permission_list(
                        eval(str(current_permission)),
                        LOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                send_message(update.effective_message, text, parse_mode="markdown")
                return (
                    "<b>{}:</b>"
                    "\n#Permission_LOCK"
                    "\n<b>Admin:</b> {}"
                    "\nLocked <code>{}</code>.".format(
                        html.escape(chat.title),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            else:
                send_message(
                    update.effective_message,
                    "What are you trying to lock...? Try /locktypes for the list of lockables",
                )
        else:
            send_message(update.effective_message, "What are you trying to lock...?")

    else:
        send_message(
            update.effective_message,
            "I am not administrator or haven't got enough rights.",
        )

    return ""



@user_admin
@loggable
@typing_action
def unlock(update, context) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    if is_user_admin(chat, message.from_user.id):
        if len(args) >= 1:

            #Support for lockname(s)
            memdata = alltypes()

            if args[0].lower().endswith('s') and not args[0].lower() in memdata:
                ltype = args[0].lower()[:-1]
            elif not args[0].lower().endswith('s') and args[0].lower() + 's' in memdata:
                ltype = args[0].lower() + 's'
            else:
                ltype = args[0].lower()

            if ltype in LOCK_TYPES:
                # Connection check
                conn = connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat = dispatcher.bot.getChat(conn)
                    chat_id = conn
                    chat_name = chat.title
                    text = f"Unlocked {ltype} for everyone in {chat_name}!"
                else:
                    if update.effective_message.chat.type == "private":
                        send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat = update.effective_chat
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = f"Unlocked {ltype} for everyone!"
                sql.update_lock(chat.id, ltype, locked=False)
                send_message(update.effective_message, text, parse_mode="markdown")
                return (
                    "<b>{}:</b>"
                    "\n#UNLOCK"
                    "\n<b>Admin:</b> {}"
                    "\nUnlocked <code>{}</code>.".format(
                        html.escape(chat.title),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )

            elif ltype in UNLOCK_CHAT_RESTRICTION:
                # Connection check
                conn = connected(context.bot, update, chat, user.id, need_admin=True)
                if conn:
                    chat = dispatcher.bot.getChat(conn)
                    chat_id = conn
                    chat_name = chat.title
                    text = f"Unlocked {ltype} for everyone in {chat_name}!"
                else:
                    if update.effective_message.chat.type == "private":
                        send_message(
                            update.effective_message,
                            "This command is meant to use in group not in PM",
                        )
                        return ""
                    chat = update.effective_chat
                    chat_id = update.effective_chat.id
                    chat_name = update.effective_message.chat.title
                    text = f"Unlocked {ltype} for everyone!"

                can_change_info = chat.get_member(context.bot.id).can_change_info
                if not can_change_info:
                    send_message(
                        update.effective_message,
                        "I don't have permission to change group info.",
                        parse_mode="markdown",
                    )
                    return

                current_permission = context.bot.getChat(chat_id).permissions
                context.bot.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=get_permission_list(
                        eval(str(current_permission)),
                        UNLOCK_CHAT_RESTRICTION[ltype.lower()],
                    ),
                )

                send_message(update.effective_message, text, parse_mode="markdown")

                return (
                    "<b>{}:</b>"
                    "\n#UNLOCK"
                    "\n<b>Admin:</b> {}"
                    "\nUnlocked <code>{}</code>.".format(
                        html.escape(chat.title),
                        mention_html(user.id, user.first_name),
                        ltype,
                    )
                )
            else:
                send_message(
                    update.effective_message,
                    "What are you trying to unlock...? Try /locktypes for the list of lockables.",
                )

        else:
            send_message(update.effective_message, "What are you trying to unlock...?")

    return ""



@user_not_admin
def del_lockables(update, context):
    chat = update.effective_chat 
    message = update.effective_message 
    user = update.effective_user
    if is_approved(chat.id, user.id):
        return
    for lockable, filter in LOCK_TYPES.items():
        if lockable == "rtl":
            if sql.is_locked(chat.id, lockable) and can_delete(chat, context.bot.id):
                if message.caption:
                    check = ad.detect_alphabet(f"{message.caption}")
                    if "ARABIC" in check:
                        try:
                            message.delete()
                        except BadRequest as excp:
                            if excp.message == "Message to delete not found":
                                pass
                            else:
                                LOGGER.exception("ERROR in lockables")
                        break
                if message.text:
                    check = ad.detect_alphabet(f"{message.text}")
                    if "ARABIC" in check:
                        try:
                            message.delete()
                        except BadRequest as excp:
                            if excp.message == "Message to delete not found":
                                pass
                            else:
                                LOGGER.exception("ERROR in lockables")
                        break
            continue
        if lockable == "button":
            if sql.is_locked(chat.id, lockable) and can_delete(chat, context.bot.id):
                if message.reply_markup and message.reply_markup.inline_keyboard:
                    try:
                        message.delete()
                    except BadRequest as excp:
                        if excp.message == "Message to delete not found":
                            pass
                        else:
                            LOGGER.exception("ERROR in lockables")
                    break
            continue
        if lockable == "inline":
            if sql.is_locked(chat.id, lockable) and can_delete(chat, context.bot.id):
                if message and message.via_bot:
                    try:
                        message.delete()
                    except BadRequest as excp:
                        if excp.message == "Message to delete not found":
                            pass
                        else:
                            LOGGER.exception("ERROR in lockables")
                    break
            continue
        if (
            filter(update)
            and sql.is_locked(chat.id, lockable)
            and can_delete(chat, context.bot.id)
        ):
            if lockable == "bots":
                new_members = update.effective_message.new_chat_members
                for new_mem in new_members:
                    if new_mem.is_bot:
                        if not is_bot_admin(chat, context.bot.id):
                            send_message(
                                update.effective_message,
                                "I see a bot and I've been told to stop them from joining..."
                                "but I'm not admin!",
                            )
                            return

                        chat.kick_member(new_mem.id)
                        send_message(
                            update.effective_message,
                            "Only admins are allowed to add bots in this chat! Get outta here.",
                        )
                        break
            else:
                try:
                    message.delete()
                except BadRequest as excp:
                    if excp.message == "Message to delete not found":
                        pass
                    else:
                        LOGGER.exception("ERROR in lockables")

                break


def build_lock_message(chat_id):
    locks = sql.get_locks(chat_id)
    res = ""
    locklist = []
    permslist = []
    if locks:
        res += "*" + "These are the current locks in this Chat:" + "*"
        if locks:
            locklist.append("sticker = `{}`".format("Locked" if locks.sticker else "Unlocked"))
            locklist.append("audio = `{}`".format("Locked" if locks.audio else "Unlocked"))
            locklist.append("voice = `{}`".format("Locked" if locks.voice else "Unlocked"))
            locklist.append("document = `{}`".format("Locked" if locks.document else "Unlocked"))
            locklist.append("video = `{}`".format("Locked" if locks.video else "Unlocked"))
            locklist.append("contact = `{}`".format("Locked" if locks.contact else "Unlocked"))
            locklist.append("photo = `{}`".format("Locked" if locks.photo else "Unlocked"))
            locklist.append("gif = `{}`".format("Locked" if locks.gif else "Unlocked"))
            locklist.append("url = `{}`".format("Locked" if locks.url else "Unlocked"))
            locklist.append("bots = `{}`".format("Locked" if locks.bots else "Unlocked"))
            locklist.append("forward = `{}`".format("Locked" if locks.forward else "Unlocked"))
            locklist.append("game = `{}`".format("Locked" if locks.game else "Unlocked"))
            locklist.append("location = `{}`".format("Locked" if locks.location else "Unlocked"))
            locklist.append("rtl = `{}`".format("Locked" if locks.rtl else "Unlocked"))
            locklist.append("button = `{}`".format("Locked" if locks.button else "Unlocked"))
            locklist.append("egame = `{}`".format("Locked" if locks.egame else "Unlocked"))
            locklist.append("inline = `{}`".format("Locked" if locks.inline else "Unlocked"))
    permissions = dispatcher.bot.get_chat(chat_id).permissions
    permslist.append("messages = `{}`".format("Unlocked" if permissions.can_send_messages else "Locked"))
    permslist.append("media = `{}`".format("Unlocked" if permissions.can_send_media_messages else "Locked"))
    permslist.append("poll = `{}`".format("Unlocked" if permissions.can_send_polls else "Locked"))
    permslist.append("other = `{}`".format("Unlocked" if permissions.can_send_other_messages else "Locked"))
    permslist.append("previews = `{}`".format("Unlocked" if permissions.can_add_web_page_previews else "Locked"))
    permslist.append("info = `{}`".format("Unlocked" if permissions.can_change_info else "Locked"))
    permslist.append("invite = `{}`".format("Unlocked" if permissions.can_invite_users else "Locked"))
    permslist.append("pin = `{}`".format("Unlocked" if permissions.can_pin_messages else "Locked"))

    if locklist:
        # Ordering lock list
        locklist.sort()
        # Building lock list string
        for x in locklist:
            res += f"\n • {x}"
    res += "\n\n*" + "These are the current chat permissions:" + "*"
    for x in permslist:
        res += f"\n • {x}"
    return res



@user_admin
@typing_action
def list_locks(update, context):
    chat = update.effective_chat 
    user = update.effective_user

    # Connection check
    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_name = chat.title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "This command is meant to use in group not in PM",
            )
            return ""
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    res = build_lock_message(chat.id)
    if conn:
        res = res.replace("Locks in", f"*{chat_name}*")

    send_message(update.effective_message, res, parse_mode=ParseMode.MARKDOWN)


def get_permission_list(current, new):
    permissions = {
        "can_send_messages": None,
        "can_send_media_messages": None,
        "can_send_polls": None,
        "can_send_other_messages": None,
        "can_add_web_page_previews": None,
        "can_change_info": None,
        "can_invite_users": None,
        "can_pin_messages": None,
    }
    permissions.update(current)
    permissions.update(new)
    new_permissions = ChatPermissions(**permissions)
    return new_permissions


def __import_data__(chat_id, data):
    # set chat locks
    locks = data.get("locks", {})
    for itemlock in locks:
        if itemlock in LOCK_TYPES:
            sql.update_lock(chat_id, itemlock, locked=True)
        elif itemlock in LOCK_CHAT_RESTRICTION:
            sql.update_restriction(chat_id, itemlock, locked=True)
        else:
            pass


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return build_lock_message(chat_id)


__help__ = """
Do stickers annoy you? or want to avoid people sharing links? or pictures? \
You're in the right place!
The locks module allows you to lock away some common items in the \
telegram world; the bot will automatically delete them!
 ‣ `/locktypes`*:* Lists all possible locktypes
*Admins only:*
 ‣ `/lock <type>`*:* Lock items of a certain type (not available in private)
 ‣ `/unlock <type>`*:* Unlock items of a certain type (not available in private)
 ‣ `/locks`*:* The current list of locks in this chat.
Locks can be used to restrict a group's users.
eg:
Locking urls will auto-delete all messages with urls, locking stickers will restrict all \
non-admin users from sending stickers, etc.
Locking bots will stop non-admins from adding bots to the chat.
*Note:*
 ‣ Unlocking permission *info* will allow members (non-admins) to change the group information, such as the description or the group name
 ‣ Unlocking permission *pin* will allow members (non-admins) to pinned a message in a group
"""

__mod_name__ = "Locks"

LOCKTYPES_HANDLER = DisableAbleCommandHandler("locktypes", locktypes, run_async=True)
LOCK_HANDLER = CommandHandler("lock", lock, pass_args=True, run_async=True)  # , filters=Filters.group)
UNLOCK_HANDLER = CommandHandler(
    "unlock", unlock, pass_args=True, run_async=True
)  # , filters=Filters.group)
LOCKED_HANDLER = CommandHandler("locks", list_locks, run_async=True)  # , filters=Filters.group)

dispatcher.add_handler(LOCK_HANDLER)
dispatcher.add_handler(UNLOCK_HANDLER)
dispatcher.add_handler(LOCKTYPES_HANDLER)
dispatcher.add_handler(LOCKED_HANDLER)

dispatcher.add_handler(
    MessageHandler(Filters.all & Filters.chat_type.group, del_lockables), PERM_GROUP,
)