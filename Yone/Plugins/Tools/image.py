import os
import cv2
from io import BytesIO
from Yone import dispatcher
from Yone.Plugins.disable import DisableAbleCommandHandler
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, run_async

# Copyright - All Copyrights of this file is belong to kushal

def sketch(update: Update, context: CallbackContext):
    bot = context.bot
    chat_id = update.effective_chat.id
    message = update.effective_message
    try:
        if message.reply_to_message and message.reply_to_message.photo:
                file_id = message.reply_to_message.photo[-1].file_id
                newFile = context.bot.get_file(file_id)
                newFile.download("getSketchfile.png")
                #reading image
                image = cv2.imread("getSketchfile.png")
                #converting BGR image to grayscale
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                #image inversion
                inverted_image = 255 - gray_image

                blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
                inverted_blurred = 255 - blurred
                pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=120.0)


                filename = 'my_sketch.png'
                cv2.imwrite(filename, pencil_sketch)
                ofile = open(filename, "rb")
                bot.send_photo(chat_id, ofile)
                if os.path.exists("getSketchfile.png"):
                    os.remove("getSketchfile.png")
                if os.path.exists(filename):
                    os.remove(filename)

        else:
            update.effective_message.reply_text(
                "Please reply to an image to make a sketch.",
            )

    except Exception as e:
      message.reply_text(f'Error Report @Yone_Support, {e}')



__help__ = """
 ‣ `/sktech `*:*  Create your image sktech by replying picture

 """

__mod_name__ = "Image"

SKETCH_HANDLER = DisableAbleCommandHandler("sketch", sketch, run_async=True)
dispatcher.add_handler(SKETCH_HANDLER)
