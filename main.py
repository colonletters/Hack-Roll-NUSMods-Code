import os

import telebot, requests, json
from telebot.types import (BotCommand, InlineKeyboardButton,
                           InlineKeyboardMarkup, LabeledPrice)

# import cart from the database file
from database import cart

# HackNRoll NUS Mods bot
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('addmodule', 'Adds a module to the timetable plan'),
    BotCommand('deletemodule', 'Deletes a module from the timetable plan'),
    BotCommand('mymodules', 'Lists all modules added to the timetable plan'),
    # BotCommand('cart', 'Lists all items added in cart'),
    # BotCommand('clearallmodules', 'Clears all items in the cart'),
])

# NUS mods database
db = requests.get("https://api.nusmods.com/v2/2021-2022/moduleList.json")

# gets all module codes to a list
lst = []
for i in db.json():
    x = i.get('moduleCode')
    lst.append(x)

# list for adding mods of interest
mymods = []


def request_start(chat_id):
    """
  Helper function to request user to execute command /start
  """
    if chat_id not in cart:
        bot.send_message(chat_id=chat_id,
          text='Please start the bot by sending /start')

    return


@bot.message_handler(commands=['start'])
def start(message):
    """
  Command that welcomes the user and configures the required initial setup
  """

    chat_id = message.chat.id

    if message.chat.type == 'private':
        chat_user = message.chat.first_name
    else:
        chat_user = message.chat.title

    message_text = f'Hello {chat_user}, welcome to NUS Mods Planner. This bot aims to help you to make your timetable in NUS as painful OR painless as possible 😄'

    # Initialise session
    cart[chat_id] = {}

    # send message to the user
    bot.send_message(chat_id=chat_id, text=message_text)


bot.infinity_polling()