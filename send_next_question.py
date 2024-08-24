from telebot import types
from bots import bot
def send_next_question(message, game):
    question = game.current_round.get_next_question()
    if question:
        markup = types.InlineKeyboardMarkup()
        if question.question_type == "multiple_choice":
            for option in question.options:
                markup.add(types.InlineKeyboardButton(text=option, callback_data=option))
        markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="continue"))
        bot.send_message(message.chat.id, question.text, reply_markup=markup)
        for player_id in game.players:
            if question.question_type == "multiple_choice":
                bot.send_message(player_id, question.text, reply_markup=markup)
            else:
                bot.send_message(player_id, question.text)
    else:
        bot.send_message(message.chat.id, "Вопросы в этом раунде закончились.")
        bot.send_message(message.chat.id, "Завершите раунд командой /end_round")