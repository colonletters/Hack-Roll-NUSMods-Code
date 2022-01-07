import os

import telebot, requests, json
from telebot.types import (BotCommand, InlineKeyboardButton,
                           InlineKeyboardMarkup, LabeledPrice)

# import cart from the database file
from database import cart

# HackNRoll NUS Mods bot
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)