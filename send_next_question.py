from telebot import types
from bots import bot
def send_next_question(message, game):
    question = game.get_current_round().get_next_question()
    if question:
        markup = types.InlineKeyboardMarkup(row_width=2)
        if question.question_type == "multiple_choice":
            for option in question.options:
                markup.add(types.InlineKeyboardButton(text=option, callback_data=option))
        for player_id in game.players:
            if question.question_type == "multiple_choice":
                bot.send_message(player_id, question.text, reply_markup=markup)
            else:
                bot.send_message(player_id, question.text)
        markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="continue"))
        text_for_admin = question.text 
        if question.question_type != "multiple_choice":
            text_for_admin += question.correct_answer
        bot.send_message(message.chat.id, text_for_admin, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вопросы в этой кончились закончились.")
        bot.send_message(message.chat.id, "Завершите раунд командой /end_game")