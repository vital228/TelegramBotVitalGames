from telebot import types
from bots import bot, send_question_materials, send_message


def send_next_question(message, game, player = None):
    question = game.get_current_round().get_next_question()
    if question:
        markup = types.InlineKeyboardMarkup(row_width=2)
        if question.question_type == "multiple_choice":
            for option in question.options:
                markup.add(types.InlineKeyboardButton(text=option, callback_data=f"multianswer_{option}"))
        if question.question_type == "open_topic":
            markup.add(types.InlineKeyboardButton(text="-", callback_data=f"minus_{player}"),
                       types.InlineKeyboardButton(text="+", callback_data=f"plus_{player}"))
            send_message(player, question.text)
            message_a = send_message(game.admin_id, f'{question.text}\nПравильный ответ: {question.correct_answer}', reply_markup=markup)
            bot.delete_message(message_a.chat.id, message_a.message_id - 2)
            return
        for player_id in game.players:
            send_question_materials(player_id, question)
            if question.question_type == "multiple_choice":
                send_message(player_id, question.text, reply_markup=markup)
            else:
                send_message(player_id, question.text)
        if question.question_type == "pentagon":
            markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_hint"))
        else:
            markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="continue"))
        text_for_admin = question.text 
        if question.question_type != "multiple_choice":
            text_for_admin += question.correct_answer
        send_question_materials(message.chat.id, question)
        send_message(message.chat.id, text_for_admin, reply_markup=markup)
            
    else:
        send_message(message.chat.id, "Вопросы в этой кончились закончились.")
        send_message(message.chat.id, "Завершите раунд командой /end_round")
        if (game.get_current_round().type == "topics"):
            bot.delete_message(message.chat.id, message.message_id)
            round = game.get_current_round()
            if round.timer_minute:
                round.timer_minute.cancel()
                round.timer_minute = None

def send_next_hint(message, game):
    question = game.get_current_round().get_current_question()
    hint = question.next_hint()
    if hint:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for player_id in game.players:
            send_message(player_id, hint)
        markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_hint"))
        send_message(message.chat.id, hint, reply_markup=markup)
    else:
        for player_id in game.players:
            send_message(player_id, f"Вопрос закончен. \nПравильный ответ:{question.correct_answer}")
        send_message(message.chat.id, "Вопрос закончен.")
        send_next_question(message, game)
