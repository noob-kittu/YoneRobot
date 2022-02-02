from emoji import UNICODE_EMOJI
#from google_trans_new import LANGUAGES, google_translator
from telegram import  Update, ParseMode 
from telegram.ext import run_async ,CallbackContext
from gpytranslate import SyncTranslator
from Yone import dispatcher
from Yone.Plugins.disable import DisableAbleCommandHandler
trans = SyncTranslator()
 
def totranslate(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text(
            "Reply to messages or write messages from other languages ​​for translating into the intended language\n\n"
            "Example: `/tr en-ja` to translate from English to Japanese\n"
            "Or use: `/tr ja` for automatic detection and translating it into japanese.\n"
            "See [List of Language Codes](t.me/fateunionupdates/32) for a list of language codes.",
            parse_mode="markdown",
            disable_web_page_preview=True)
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = trans(to_translate,
                              sourcelang=source, targetlang=dest)
    reply = f"<b>Translated from {source} to {dest}</b>:\n" \
        f"<code>{translation.text}</code>"
 
    message.reply_text(reply, parse_mode=ParseMode.HTML)
 
 
__help__ = """ You can translate messages on telegram in a simple way
‣ `/tr [List of Language Codes]`:- as reply to a long message.
‣ `/tl [List of Language Codes]`:- as reply to a long message.
"""
__mod_name__ = "Translator"
 
TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], totranslate, run_async=True)
 
dispatcher.add_handler(TRANSLATE_HANDLER)
 
__command_list__ = ["tr", "tl"]
__handlers__ = [TRANSLATE_HANDLER]
 