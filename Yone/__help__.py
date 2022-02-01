import importlib, re
from Yone import dispatcher, ALLOW_EXCL, LOGGER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from Yone.Handlers.misc import paginate_modules
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown
from Yone.Handlers.validation import is_user_admin
from telegram.ext.dispatcher import DispatcherHandlerStop
from os.path import isfile


HELP_STRINGS = """Hey there! My name is *{}*.
I'm a modular group management bot with a few fun extras! Have a look at the following for an idea of some of the things I can help you with. """.format(
    dispatcher.bot.first_name, ""
    if not ALLOW_EXCL else "\nAll commands can either be used with / or !.\n")

IMPORTED = {}
ADMIN_IMPORTED = {}
USER_IMPORTED = {}
TOOLS_IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
ADMIN = {}
USER = {}
TOOLS = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

import os
path =r'Yone/Plugins/'
list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        list_of_files.append(os.path.join(root,file))

mod_name = [
        name[:-3].replace("/", ".").replace("\\", ".")
        for name in list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]


path =r'Yone/Plugins/Admin/'
admin_list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        admin_list_of_files.append(os.path.join(root,file))

admin_mod_name = [
        name[:-3].replace("/", ".").replace("\\", ".")
        for name in admin_list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]

for module_names in admin_mod_name:
    admin_imported_module = importlib.import_module(module_names)
    if not hasattr(admin_imported_module, "__mod_name__"):
        admin_imported_module.__mod_name__ = admin_imported_module.__name__

    if admin_imported_module.__mod_name__.lower() not in ADMIN_IMPORTED:
        ADMIN_IMPORTED[admin_imported_module.__mod_name__.lower()] = admin_imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(admin_imported_module, "__help__") and admin_imported_module.__help__:
        ADMIN[admin_imported_module.__mod_name__.lower()] = admin_imported_module

path =r'Yone/Plugins/User/'
user_list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        user_list_of_files.append(os.path.join(root,file))

user_mod_name = [
        name[:-3].replace("/", ".").replace("\\", ".")
        for name in user_list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]

for u_module_names in user_mod_name:
    user_imported_module = importlib.import_module(u_module_names)
    if not hasattr(user_imported_module, "__mod_name__"):
        user_imported_module.__mod_name__ = user_imported_module.__name__

    if user_imported_module.__mod_name__.lower() not in USER_IMPORTED:
        USER_IMPORTED[user_imported_module.__mod_name__.lower()] = user_imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(user_imported_module, "__help__") and user_imported_module.__help__:
        USER[user_imported_module.__mod_name__.lower()] = user_imported_module


path =r'Yone/Plugins/Tools/'
tools_list_of_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        tools_list_of_files.append(os.path.join(root,file))

tools_mod_name = [
        name[:-3].replace("/", ".").replace("\\", ".")
        for name in tools_list_of_files
        if isfile(name) and name.endswith(".py") and not name.endswith("__init__.py")
    ]

for t_module_name in tools_mod_name:
    tools_imported_module = importlib.import_module(t_module_name)
    if not hasattr(tools_imported_module, "__mod_name__"):
        tools_imported_module.__mod_name__ = tools_imported_module.__name__

    if tools_imported_module.__mod_name__.lower() not in TOOLS_IMPORTED:
        TOOLS_IMPORTED[tools_imported_module.__mod_name__.lower()] = tools_imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(tools_imported_module, "__help__") and tools_imported_module.__help__:
        TOOLS[tools_imported_module.__mod_name__.lower()] = tools_imported_module

for module_name in mod_name:
    imported_module = importlib.import_module(module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


def send_admin_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, ADMIN, "admin"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )

def send_user_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, USER, "user"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )

def send_tools_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, TOOLS, "tools"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )

def admin_help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"admin_module\((.+?)\)", query.data)
    prev_match = re.match(r"admin_prev\((.+?)\)", query.data)
    next_match = re.match(r"admin_next\((.+?)\)", query.data)
    back_match = re.match(r"admin_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    ADMIN[module].__mod_name__
                )
                + ADMIN[module].__help__
            )
            query.message.edit_text( 
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [ 
                      [InlineKeyboardButton(text="Back", callback_data="admin_back")]
                        
                    ]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, ADMIN, "admin")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, ADMIN, "admin")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, ADMIN, "admin")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def user_help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"user_module\((.+?)\)", query.data)
    prev_match = re.match(r"user_prev\((.+?)\)", query.data)
    next_match = re.match(r"user_next\((.+?)\)", query.data)
    back_match = re.match(r"user_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    USER[module].__mod_name__
                )
                + USER[module].__help__
            )
            query.message.edit_text( 
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [ 
                      [InlineKeyboardButton(text="Back", callback_data="user_back")]
                        
                    ]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, USER, "user")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, USER, "user")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, USER, "user")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def tools_help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"tools_module\((.+?)\)", query.data)
    prev_match = re.match(r"tools_prev\((.+?)\)", query.data)
    next_match = re.match(r"tools_next\((.+?)\)", query.data)
    back_match = re.match(r"tools_back", query.data)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    TOOLS[module].__mod_name__
                )
                + TOOLS[module].__help__
            )
            query.message.edit_text( 
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [ 
                      [InlineKeyboardButton(text="Back", callback_data="tools_back")]
                        
                    ]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, TOOLS, "tools")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, TOOLS, "tools")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, TOOLS, "tools")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass

def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text( 
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [ 
                      [InlineKeyboardButton(text="Back", callback_data="help_back")]
                        
                    ]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


# Settings Command Function Starting From Here 
def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )

def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))

def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat 
    user = update.effective_user 
    msg = update.effective_message  

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop
