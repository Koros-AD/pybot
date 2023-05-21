import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import cv2
from io import BytesIO
import numpy as np
TOKEN='6052151725:AAGP3XjlbSqNVLtY8ORUZJsEht7NKOB0wng'
bot=telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start','help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, f'Welcome, {message.chat.username}. This is CoolBot2023.')

@bot.message_handler(content_types=['document','audio'])
def say_lmao(message:telebot.types.Message):
    bot.reply_to(message,'Nice doc')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Get the photo from the message
    photo = message.photo[-1]  # Use the last (highest resolution) photo

    # Download the photo
    file_info = bot.get_file(photo.file_id)
    file = bot.download_file(file_info.file_path)

    # Convert the photo to black and white
    image = cv2.imdecode(np.frombuffer(file, np.uint8), -1)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Encode the black and white image to JPEG
    _, buffer = cv2.imencode('.jpg', gray_image)
    file_bytes = BytesIO(buffer.tobytes())

    # Send the black and white image back to the user
    bot.send_photo(message.chat.id, file_bytes)

bot.polling(none_stop=True)