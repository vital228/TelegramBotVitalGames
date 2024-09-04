from threading import Timer
from bots import bot
from telebot import types
from Question import load_questions_from_file
import random
def start_topic_round(game, topic):
    round = game.get_current_round()
    p_id = round.queue_players.get()
    admin_id = game.admin_id
    round.queue_players.put(p_id)
    for t in round.topics:
        if t['round']==topic:
            t['is_played']=True
    round.timer_minute = Timer(60, end_round, [round])
    round.questions = load_questions_from_file(f'game_1/{topic}.json')
    random.shuffle(round.questions)
    round.current_question_index = 0
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Начать", callback_data=f"start_{p_id}"))
    bot.send_message(admin_id, f'Тема: {topic}, у вас ровно 60 секунд', reply_markup=markup)
    bot.send_message(p_id, f'Тема: {topic}, у вас ровно 60 секунд')


def end_round(round):
    round.questions.clear()
