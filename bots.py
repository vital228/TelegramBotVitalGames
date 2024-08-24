import telebot

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

games = {}