from telebot import types
from bots import bot
from get_game_by import get_game_by_message
from send_next_question import send_next_question

@bot.callback_query_handler(func=lambda call: True)
def handle_answer(call):
    game = get_game_by_message(call)
    if not game or not game.current_round:
        return

    current_question = game.current_round.questions[game.current_round.current_question_index - 1]
    
    if call.data == "continue":
        if call.from_user.id == game.admin_id:
            if current_question.question_type == "multiple_choice":
                correct_count = sum(1 for answer in current_question.answers.values() if answer == current_question.correct_answer)
                bot.send_message(call.message.chat.id, f"{correct_count} игрок(ов) ответили правильно.")
            elif current_question.question_type == "open":
                unique_answers = set(current_question.answers.values())
                markup = types.InlineKeyboardMarkup()
                for answer in unique_answers:
                    markup.add(types.InlineKeyboardButton(text=answer, callback_data=f"correct_{answer}"))
                markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_question"))
                bot.send_message(call.message.chat.id, "Уникальные ответы игроков:", reply_markup=markup)
            send_next_question(call.message, game)  # Переход к следующему вопросу
    elif call.data.startswith("correct_"):
        if call.from_user.id == game.admin_id:
            correct_answer = call.data[len("correct_"):]
            for player_id, answer in current_question.answers.items():
                if answer == correct_answer:
                    game.players[player_id]["score"] += 1
            bot.send_message(call.message.chat.id, f"Ответ '{correct_answer}' отмечен как правильный.")
    elif call.data == "next_question":
        if call.from_user.id == game.admin_id:
            send_next_question(call.message, game)
    else:
        player_id = call.from_user.id
        if player_id in game.players:
            current_question.answers[player_id] = call.data
            bot.send_message(call.message.chat.id, f"Ваш ответ '{call.data}' принят.")
            if current_question.question_type == "multiple_choice" and current_question.check_answer(call.data):
                game.players[player_id]["score"] += 1
            bot.send_message(game.admin_id, f"Игрок {game.players[player_id]['name']} ответил: {call.data}")

@bot.message_handler(func=lambda message: True)
def handle_open_question(message):
    game = get_game_by_message(message)
    if game and game.current_round:
        current_question = game.current_round.questions[game.current_round.current_question_index - 1]
        if current_question.question_type == "open":
            current_question.answers[message.from_user.id] = message.text
            bot.send_message(message.chat.id, "Ваш ответ принят.")
            bot.send_message(game.admin_id, f"Игрок {game.players[message.from_user.id]['name']} ответил: {message.text}")
