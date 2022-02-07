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
    message = update.effective_message
    if message.reply_to_message and message.reply_to_message.photo:
            file_id = message.reply_to_message.photo[-1].file_id
            with BytesIO() as file:
                file.name = 'getSketchfile.png'
                new_file = bot.get_file(file_id)
                new_file.download(out=file)
                file.seek(0)
                #reading image
                image = cv2.imread(file)
                #converting BGR image to grayscale
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                #image inversion
                inverted_image = 255 - gray_image

                blurred = cv2.GaussianBlur(inverted_image, (21, 21), 0)
                inverted_blurred = 255 - blurred
                pencil_sketch = cv2.divide(gray_image, inverted_blurred, scale=120.0)


                filename = 'Sketch.jpg'
                cv2.imwrite(filename, pencil_sketch)
                ofile = open(filename, "rb")
                message.reply_photo(
                        ofile,
                        caption="Made By @Yone_Robot",
                        parse_mode=ParseMode.HTML,
                        
                    )
                if os.path.exists(file.name):
                    os.remove(file.name)
                if os.path.exists(filename):
                    os.remove(filename)

    else:
        update.effective_message.reply_text(
            "Please reply to an image to make a sketch.",
        )



__help__ = """
 ‣ `/sktech `*:*  Create your image sktech by replying picture

 """

__mod_name__ = "Image"

SKETCH_HANDLER = DisableAbleCommandHandler("sketch", sketch, run_async=True)
dispatcher.add_handler(SKETCH_HANDLER)
