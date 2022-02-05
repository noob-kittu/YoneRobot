from Yone import dispatcher, SUPPORT_CHAT

try:
    import os
    import wn
    import html
    from telegram import ParseMode, Update
    from telegram.ext import CallbackContext, run_async
    from Yone.Plugins.disable import DisableAbleCommandHandler
    LEXICON_NAME = 'ewn:2020'
    LEXICON_DL = 'https://media.githubusercontent.com/media/AnimeKaizoku/WordNet/ewn_2021/ewn_2021.bin'
    wn.config.allow_multithreading = True
    wn.config.data_directory = os.path.abspath('wn_data')
    wn.download(LEXICON_DL, progress_handler=None)

    def dictionary(update: Update, context: CallbackContext):
        message = update.effective_message
        word = message.text[len('/dict ') :].strip()
        senses = wn.senses(word, lexicon=LEXICON_NAME)
        if not senses:
            message.reply_text('No results found')
            return
        word = senses[0].word().lemma()
        meanings, synonyms, antonyms, examples = [], [], [], []
        for sense in senses:
            meanings.append(sense.synset().definition())
            synonyms.extend(i.lemma() for i in sense.synset().words() if i.lemma() != sense.word().lemma())
            antonyms.extend(i.word().lemma() for i in sense.get_related('antonym') if i.word().lemma() != sense.word().lemma())
            examples.extend(sense.synset().examples())
        # no idea why this is here and why 4 but it is what it is
        meanings = meanings[:4]
        synonyms = synonyms[:4]
        antonyms = antonyms[:4]
        examples = examples[:4]

        reply_text = f'ℹ️ <b>Word Dictionary</b>\n\n<b>Possible Meanings for "{html.escape(word)}":</b>\n'
        for i in meanings:
            reply_text += f'• <code>{html.escape(i)}</code>\n'
        reply_text += '\n'
        if synonyms:
            reply_text += f'<b>Synonyms:</b> {", ".join(f"<code>{html.escape(i)}</code>" for i in synonyms)}\n'
        if antonyms:
            reply_text += f'<b>Antonyms:</b> {", ".join(f"<code>{html.escape(i)}</code>" for i in antonyms)}\n'
        if examples:
            reply_text += f'<b>Examples:</b>\n'
            for i in examples:
                reply_text += f'• <code>{html.escape(i)}</code>\n'

        message.reply_text(reply_text, parse_mode=ParseMode.HTML)


    DICT_HANDLER = DisableAbleCommandHandler(["dict"], dictionary, run_async=True)

    dispatcher.add_handler(DICT_HANDLER)

    __mod_name__ = "Dictionary"
    __command_list__ = ["dict"]
    __handlers__ = [DICT_HANDLER]
except:
    dispatcher.bot.send_message(f"@{SUPPORT_CHAT}", "Failed to load dictionary module.")