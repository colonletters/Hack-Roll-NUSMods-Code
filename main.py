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
    BotCommand('clearmodules', 'Clears all module from module cart'),
    BotCommand('mymodules', 'Lists all modules added to the timetable plan'),
    BotCommand('checkslots', 'Checks the vacancy of the mods in the cart'),
    BotCommand('surpriseme', 'Surprises!')
])

# NUS mods database
db = requests.get("https://api.nusmods.com/v2/2021-2022/moduleList.json")

# gets all module codes to a list
lst = []
for i in db.json():
    x = i.get('moduleCode')
    lst.append(x)

# list for adding mods of interest
# mymods = []


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

  # Initialise mymods list specific to the user
  cart[chat_id]["mymods"] = []

  # send message to the user
  bot.send_message(chat_id=chat_id, text=message_text)


# add module to a list
@bot.message_handler(commands=['addmodule'])
def modadd(message):
  """
  Command that adds modules to the list
  """

  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return

  try:
      msg = message.text.split()
      modname = msg[1].upper()
      mymods = cart[chat_id]["mymods"]

      # error if module alr in the list
      if modname in mymods:
        bot.send_message(chat_id, text='Module already added!')        

      # check if module is in the NUSmods list
      elif modname in lst:
          mymods.append(modname)
          print(modname)  # error checking purposes, to delete
          bot.reply_to(message, modname)
          bot.send_message(
              chat_id,
              text=
              'Module successfully added! Continue to add modules using the format /addmodule <module code>. e.g. /addmodule LSM2191. To check the list of modules added, use the command /mymodules'
          )
      
  # returns error if not in list
      else:
          bot.send_message(chat_id, text='Please enter a valid module code!')

  # error message if they do not give a module code after the command
  except:
      bot.send_message(
          chat_id,
          text=
          'Please enter a module code in this format: /addmodule <module code>. e.g. /addmodule LSM2191'
      )


# del module from a list
@bot.message_handler(commands=['deletemodule'])
def moddel(message):
  """
  Command that deletes modules to the list
  """
  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return

  try:
      msg = message.text.split()
      modname = msg[1].upper()
      mymods = cart[chat_id]["mymods"]

      # check if module is in own list
      if modname in mymods:
          print(modname)  # error checking purposes, to delete
          mymods.remove(modname)
          bot.reply_to(message, modname)
          bot.send_message(
              chat_id,
              text=
              'Module successfully removed! Continue to delete modules using the format /deletemodule <module code>. e.g. /deletemodule LSM2191. To check the list of modules added, use the command /mymodules'
          )

      # returns error if not in list
      else:
          bot.send_message(chat_id, text='Module was not added!')

  # error message if they do not give a module code after the command
  except:
      bot.send_message(
          chat_id,
          text=
          'Please enter a module code in this format: /deletemodule <module code>. e.g. /deletemodule LSM2191'
      )


# clear modules from module list
@bot.message_handler(commands=['clearmodules'])
def modclear(message):
  """
  Command that clear all modules from module list
  """

  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return

  cart[chat_id]["mymods"] = []
  bot.send_message(
          chat_id,
          text=
          'Module cart has been cleared!'
      )


# displays list of modules that was added by user
@bot.message_handler(commands=['mymodules'])
def mymodules(message):
  """
  Command that shows modules in the list
  """

  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return

  # prints out the list of modules added
  mymods = cart[chat_id]["mymods"]
  print(mymods)

  # check if list of mods added is empty
  if len(mymods) == 0:
    bot.send_message(
      chat_id,
      text=
      'No modules in the list!'
    )
    
  else:
    bot.send_message(chat_id, text='Here are the modules in the list now:')
  
    for i in range(len(mymods)):
      modtext = mymods[i]
      bot.send_message(chat_id, text=modtext)
    bot.send_message(
      chat_id,
      text=
      'To delete a module, use the command /deletemodule <module code>. e.g. /deletemodule LSM2191'
      )


# checks the total slots of the mods in the cart
@bot.message_handler(commands=['checkslots'])
def checkslots (message):
  """
  Checks total slots of the mods in the cart
  """

  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return
  
  mymods = cart[chat_id]["mymods"]
  
  # check if list of mods added is empty
  if len(mymods) == 0:
    bot.send_message(
      chat_id,
      text=
      'No modules in the list! Please add modules using the command /addmodule to view the vacancies'
    )

  # Get total possible slots for modules in the cart
  for mod in mymods:
    total_size = 0
    tmp_db = requests.get(f"https://api.nusmods.com/v2/2021-2022/modules/{mod}.json")

    # Narrow down data with class sizes
    timetable = tmp_db.json()["semesterData"][0]["timetable"]
    
    # Add student count for all classNo
    for i in range (1, 7):
      for j in timetable:
        if j["classNo"] == f"{i}" and j["lessonType"] == "Lecture":
          total_size += j["size"]
          break
          
    bot.send_message(
    chat_id,
    text=
    f'The total slots for {mod} is {total_size}.'
    )


# checks the total slots of the mods in the cart
@bot.message_handler(commands=['surpriseme'])
def surpriseme (message):
  """
  Surprise surprise
  """

  chat_id = message.chat.id
  if chat_id not in cart:
      request_start(chat_id)
      return
  
  bot.send_message(
      chat_id,
      text=
      'https://www.youtube.com/watch?v=oPRv6WrPThI'
      )


bot.infinity_polling()