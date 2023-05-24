import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import cv2
from io import BytesIO
import numpy as np
TOKEN='6052151725:AAGP3XjlbSqNVLtY8ORUZJsEht7NKOB0wng'
bot=telebot.TeleBot(TOKEN)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# Starting
@bot.message_handler(commands=['start'])
def handle_start_help(message):
     bot.send_message(message.chat.id, f'Greetings, {message.chat.username}. This is FindInPicBot! It can detect faces, white color and geometric shapes in pictures. '
                                      f'Send /help for more info')
# Setting up menu and buttons for commands
@bot.message_handler(commands=['menu'])
def options(message):
        keyboard = InlineKeyboardMarkup()

# Adding buttons to the keyboard
        button1 = InlineKeyboardButton("Find faces", callback_data='button1')
        button2 = InlineKeyboardButton("Find circles", callback_data='button2')
        button3= InlineKeyboardButton("Find rectangles",callback_data='button3')
        button4 = InlineKeyboardButton("Find white color %", callback_data='button4')
        keyboard.add(button1,button2,button3,button4)
        bot.send_message(message.chat.id, 'Choose an option:', reply_markup=keyboard)

# Asigning functions to buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'button1':
        bot.send_message(call.message.chat.id, 'Send input photo')
        bot.register_next_step_handler(call.message, findface)
    elif call.data == 'button2':
        bot.send_message(call.message.chat.id, 'Send input photo')
        bot.register_next_step_handler(call.message, find_circle_photo)
    elif call.data == 'button3':
        bot.send_message(call.message.chat.id, 'Send input photo')
        bot.register_next_step_handler(call.message, findrectangles)
    elif call.data == 'button4':
        bot.send_message(call.message.chat.id, 'Send input photo')
        bot.register_next_step_handler(call.message, countwhite)
#help menu
@bot.message_handler(commands=['help'])
def helpme(message:telebot.types.Message):
      bot.reply_to(message,'''Type /menu to open up the menu with all the functions, which are the following:
      1. Finding and counting faces in pictures
      2. Finding and counting circles in pictures
      3. Finding and counting rectangles in pictures
      4. Counting the percentage of white color in pictures
      Enjoy!''')
#Stoping the bot
@bot.message_handler(commands=['bye'])
def byebye(message):
    bot.reply_to(message,'Thank you! Bye.')
    bot.stop_bot()
# Wrong data type
@bot.message_handler(content_types=['document','audio','video'])
def say_lmao(message:telebot.types.Message):
      bot.reply_to(message,'Nice doc!But I only work with pictures')

# Functions
@bot.message_handler(content_types=['photo'])
# Detecting faces
def findface(message):
     photo = message.photo[-1]
     file_info = bot.get_file(photo.file_id)
     file = bot.download_file(file_info.file_path)
# Convert the photo to a format suitable for OpenCV
     nparr = np.frombuffer(file, np.uint8)
     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# Convert the image to grayscale
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Detect faces in the grayscale image
     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
# Draw rectangles around the detected faces
     num_faces=0
     for (x, y, w, h) in faces:
         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
         num_faces +=1
# Encode the image with rectangles to JPEG
     _, buffer = cv2.imencode('.jpg', image)
     file_bytes = BytesIO(buffer.tobytes())
# Send the message and the image with rectangles back to the user
     bot.send_message(message.chat.id, f'Total faces: {num_faces}')
     bot.send_photo(message.chat.id, file_bytes)
# Finding circles
def find_circle_photo(message):
     photo = message.photo[-1]
     file_info = bot.get_file(photo.file_id)
     file = bot.download_file(file_info.file_path)
     nparr = np.frombuffer(file, np.uint8)
     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
 # Convert the image to grayscale
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Apply Hough Circle Transform to detect circles
     circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=50, param2=30, minRadius=5,
                               maxRadius=500)
     if circles is not None:
        circles = np.round(circles[0, :]).astype(int)
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 2)
     num_circles=len(circles)
# Encode the modified image to JPEG to send back to the user
     _, buffer = cv2.imencode('.jpg', image)
     file_bytes = BytesIO(buffer.tobytes())
     bot.send_message(message.chat.id,f'Total circles:{num_circles}')
     bot.send_photo(message.chat.id, file_bytes)
# Finding rectangles
def findrectangles(message):
     photo = message.photo[-1]  # Use the last (highest resolution) photo
     file_info = bot.get_file(photo.file_id)
     file = bot.download_file(file_info.file_path)
# Convert the photo to a format suitable for OpenCV
     nparr = np.frombuffer(file, np.uint8)
     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# Convert the image to grayscale
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# Apply a threshold to the grayscale image
     _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
# Find contours in the thresholded image
     contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Find rectangles in the contours
     rectangles = []
     for contour in contours:
         perimeter = cv2.arcLength(contour, True)
         approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
         if len(approx) == 4:
             rectangles.append(approx)
     num_rect=len(rectangles)
# Draw rectangles on the original image
     image_with_rectangles = image.copy()
     cv2.drawContours(image_with_rectangles, rectangles, -1, (0, 255, 0), 2)
# Encode the image with rectangles to JPEG
     _, buffer = cv2.imencode('.jpg', image_with_rectangles)
     file_bytes = BytesIO(buffer.tobytes())
# Send the image with rectangles back to the user
     bot.send_message(message.chat.id,f'Total rectangles: {num_rect}')
     bot.send_photo(message.chat.id, file_bytes)

# Counting the percentage of white pixels in image
def countwhite(message):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    file = bot.download_file(file_info.file_path)
# Convert the photo to a format suitable for OpenCV
    nparr = np.frombuffer(file, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
# Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
# Calculating the white color percentage
    pixels = binary_image.size
    white_pixel = np.count_nonzero(binary_image == 255)
    pixelperc = round((white_pixel / pixels) * 100)
    bot.send_message(message.chat.id, f'Percentage of white color is: {pixelperc}%')

bot.polling(none_stop=True)
