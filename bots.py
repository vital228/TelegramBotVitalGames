import telebot

import os
from dotenv import load_dotenv
from DataBase import start, get_all_games

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
start()
games = get_all_games()
msg_ids = {}


def send_message(chat_id, text, reply_markup = None):
    msg = bot.send_message(chat_id, text, reply_markup=reply_markup)
    if chat_id not in msg_ids:
        msg_ids[chat_id] = []
    msg_ids[chat_id].append(msg.message_id)
    return msg

def add_message(chat_id, msg_id):
    if chat_id not in msg_ids:
        msg_ids[chat_id] = []
    msg_ids[chat_id].append(msg_id)

def send_question_materials(chat_id, question):
    if chat_id not in msg_ids:
        msg_ids[chat_id] = []
    if question.url_photo:
        msg = bot.send_photo(chat_id, question.url_photo)
        msg_ids[chat_id].append(msg.message_id)
    if question.url_audio:
        msg =bot.send_photo(chat_id, question.url_audio)
        msg_ids[chat_id].append(msg.message_id)
    if question.photo:
        msg = bot.send_photo(chat_id,  open(question.photo, 'rb'))
        msg_ids[chat_id].append(msg.message_id)
    if question.audio:
        msg = bot.send_audio(chat_id, open(question.audio, 'rb'))
        msg_ids[chat_id].append(msg.message_id)


def delete_all_message():
    for chat_id in msg_ids.keys():
        for msg_id in msg_ids[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение {msg_id}: {e}")