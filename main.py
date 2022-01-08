import os

import telebot, requests, json, random, re, classes
from telebot.types import (BotCommand, InlineKeyboardButton,
                           InlineKeyboardMarkup, LabeledPrice)

# import cart, NUSMods
from database import cart
from APICall import db, lst, GetModuleInfo

# HackNRoll NUS Mods bot
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)

bot.set_my_commands([
    BotCommand('start', 'Starts the bot'),
    BotCommand('addmodule', 'Adds a module to the timetable plan'),
    BotCommand('deletemodule', 'Deletes a module from the timetable plan'),
    BotCommand('clearmodules', 'Clears all module from module cart'),
    BotCommand('mymodules', 'Lists all modules added to the timetable plan'),
    BotCommand('mymoddetails', 'View more details of modules in cart')
])

CURRENT_SEMESTER = "2"
ACADEMIC_YEAR = "AY 2021/2022"

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

  # Initialise session
  cart[chat_id] = {}

  # Initialise mymods list specific to the user
  cart[chat_id]["mymods"] = []

  # send message to the user
  bot.send_message(chat_id=chat_id, text=f'Hello {chat_user}, welcome to NUS Mods Planner. This bot aims to help you to check and plan your timetable in NUS 😄')
  bot.send_message(chat_id=chat_id, text=f'To view the functions in this bot, type / and select the command of interest, e.g. /addmodule')

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
    # checks the format of the input (i.e. got commas etc)
    pattern = re.compile(r"(\w+)(,\s*\w+)*$")
    
    # remove /addmodules part and convert all to upper
    msg = message.text.replace("/addmodule ", "").upper()
    print(msg)

    # error message if not separated by comma
    if pattern.match(msg) == None:
      bot.send_message(chat_id, text=f'The module could not be added because it is not entered in the right format. Add modules using the format /addmodule <module code>. e.g. /addmodule LSM2191 OR multiple modules using e.g. /addmodule LSM2191, LSM2232. To check the list of modules added, use the command /mymodules')
      return
    
    # split by ',' and remove whitespace, modules will be in a list (if have >1 modules)
    elif ',' in msg:
      lstmods = msg.split(", ")
      # lstmods = [x.strip(' ') for x in lstmods]
    
    # if only one module in added, add to lstmods (to check if it is in NUSmods later)
    else:
      lstmods = []
      lstmods.append(msg)

    # loop through each mod in the list and error check
    for modname in lstmods:
      mymods = cart[chat_id]["mymods"]
      tmp_db = GetModuleInfo(modname)["semesterData"]
      semesters_offered = []

      # append module's offered semesters into a list
      for i in tmp_db:
        semesters_offered.append(str(i["semester"]))

      # error if module not offered in current semester
      if CURRENT_SEMESTER not in semesters_offered:
        bot.send_message(chat_id, text=f'{modname} could not be added because it is not offered in {ACADEMIC_YEAR} semester {CURRENT_SEMESTER}.')
        continue

      # error if module alr in the list
      if modname in mymods:
        bot.send_message(chat_id, text='Module already added!')
        continue
      
      # check if no of modules in the list is > 10 (have a cap)
      if len(mymods) >= 10:
        bot.send_message(
        chat_id,
        text=
        'Maximum number of modules (10) added!'
        )
        return

      # check if module is in the NUSmods list
      elif modname in lst:
        mymods.append(modname)
        print(modname)  # error checking purposes, to delete
        bot.send_message(
            chat_id,
            text=
            f'**{modname}** successfully added!'
        )
        continue
        
      # returns error if not in list
      else:
        bot.send_message(chat_id, text=f'{modname} is not a valid module code!')

    bot.send_message(chat_id, text=f'Continue to add modules using the format /addmodule <module code>. e.g. /addmodule LSM2191 OR multiple modules using e.g. /addmodule LSM2191, LSM2232. To check the list of modules added, use the command /mymodules')
    
    print(f"This is for lstmods {lstmods}")

  # error message if they do not give a module code after the command
  except:
      bot.send_message(
          chat_id,
          text=
          'Please enter a module code in this format: /addmodule <module code>. e.g. /addmodule LSM2191 OR multiple modules using /addmodule LSM2191, LSM2232 and ensure that it is a valid module offered this semester'
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
    return
    
  else:
    modtext = 'Here are the list added mods:\n'
    for i in range(len(mymods)):
      mod = mymods[i]
      modtext += f'{mod}\n'
    
    bot.send_message(
      chat_id,
      text=modtext
      )

    bot.send_message(
      chat_id,
      text=
      'To delete a module, use the command /deletemodule <module code>. e.g. /deletemodule LSM2191'
      )


# Provide buttons for functions available
@bot.message_handler(commandsmymoddetailsons'])
dmymoddetailsons(message):
  """
  Display available functions in buttons
  """

  chat_id = message.chat.id
  if chat_id not in cart:
    request_start(chat_id)
    return

  chat_text = 'Select the function you would like to execute for modules in the cart'

  buttons = []
  all_functions = [
    'Check slots',
    'Check total modular credits',
    'Can my modules be S/U-ed?',
    'Surprise me',
  ]

  for function_name in all_functions:
    row = []
    button = InlineKeyboardButton(
      function_name,
      callback_data=function_name
    )
    row.append(button)
    buttons.append(row)

  bot.send_message(
    chat_id=chat_id,
    text=chat_text,
    reply_markup=InlineKeyboardMarkup(buttons)
  )


# Handle receiving callback queries
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
  """
  Handles the execution of functions when receiving a callback query
  """

  chat_id = call.message.chat.id
  data = call.data

  if data == 'Check slots':
    checkslots(chat_id)
    return
  if data == 'Surprise me':
    surpriseme(chat_id)
    return
  if data == 'Check total modular credits':
    checkcredits(chat_id)
    return
  if data == 'Can my modules be S/U-ed?':
    checkSU(chat_id)
    return


# Helper function that checks the total slots of the mods in the cart
def checkslots(chat_id):
  """
  Checks total slots of the mods in the cart
  """
  
  mymods = cart[chat_id]["mymods"]
  
  # check if list of mods added is empty
  if len(mymods) == 0:
    bot.send_message(
      chat_id,
      text=
      'No modules in the list! Please add modules using the command /addmodule to view the slots!'
    )
    return

  # Get total possible slots for modules in the cart
  for mod in mymods:
    total_size = 0
    tmp_db = GetModuleInfo(f'{mod}')

    # Narrow down data with class sizes
    semesterData = tmp_db["semesterData"]

    # Check if semester 1 or semester 2
    for semester in semesterData:
      if semester["semester"] == 1:
        continue
      elif semester["semester"] == 2:
        timetable = semester["timetable"]
        
        # Add student count for all classNo
        for i in range (1, 30):
          for j in timetable:
            if j["classNo"] == f"{i}" and j["lessonType"] == "Lecture":
              total_size += j["size"]
              break
        
        if total_size == 0:
          for i in range (1, 30):
            for j in timetable:
              if j["classNo"] == f"{i}" and j["lessonType"] == "Tutorial":
                total_size += j["size"]
                break

        if total_size == 0:
          for i in range (1, 30):
            for j in timetable:
              if j["classNo"] == f"0{i}" and j["lessonType"] == "Sectional Teaching":
                total_size += j["size"]
                print(j["size"])
                break
              
              elif j["classNo"] == f"{i}" and j["lessonType"] == "Sectional Teaching":
                total_size += j["size"]
                print(j["size"])
                break
                
        bot.send_message(
        chat_id,
        text=
        f'The total slots for {mod} is {total_size}.'
        )
  return


# Helper function to check total credits in the cart
def checkcredits(chat_id):
  """
  Checks total credits of the mods in the cart
  """
  mymods = cart[chat_id]["mymods"]
  
  # check if list of mods added is empty
  if len(mymods) == 0:
    bot.send_message(
      chat_id,
      text=
      'No modules in the list! Please add modules using the command /addmodule to view the slots!'
    )
    return

  total_credits = 0
  
  # Calculate total credits
  for mod in mymods:
    tmp_db = GetModuleInfo(f'{mod}')
    total_credits += int(tmp_db["moduleCredit"])
  
  bot.send_message(
        chat_id,
        text=
        f'The total module credits in your cart is {total_credits}.'
        )
  return


# Helper function to check if mods are S/U-able in the cart
def checkSU(chat_id):
  """
  Checks if mods in the cart can be s/u-ed
  """
  mymods = cart[chat_id]["mymods"]
  
  # check if list of mods added is empty
  if len(mymods) == 0:
    bot.send_message(
      chat_id,
      text=
      'No modules in the list! Please add modules using the command /addmodule to view the slots!'
    )
    return

  # check mods that are s/u-able
  for mod in mymods:
    tmp_db = GetModuleInfo(f'{mod}')

    try:
      print(mod)
      attributes = tmp_db["attributes"]

      if attributes["su"] == True:
        bot.send_message(
            chat_id,
            text=
            f'You __*CAN*__ S/U {mod}',
            parse_mode='MarkdownV2'
            )
      else:
        bot.send_message(
            chat_id,
            text=
            f'You __*CANNOT*__ S/U {mod}',
            parse_mode='MarkdownV2'
            )
    
    except:
      print(mod)
      bot.send_message(
          chat_id,
          text=
          f'You __*CANNOT*__ S/U {mod}',
          parse_mode='MarkdownV2'
          )
  return


# Helper function that surprises the user
def surpriseme(chat_id):
  """
  Surprise surprise
  """

  # Rick roll, vaccination
  surprises = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=oPRv6WrPThI"
  ]

  
  # Generate random URL
  random_url = surprises[random.randrange(len(surprises))]

  bot.send_message(
      chat_id,
      text=f'{random_url}'
      )
  return


bot.infinity_polling()