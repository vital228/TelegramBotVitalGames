from telebot import types
from bots import bot, add_message, send_message
from get_game_by import get_game_by_message
from send_next_question import send_next_question, send_next_hint
from topics_round import start_topic_round
from Question import Question

@bot.callback_query_handler(func=lambda call: True)
def handle_answer(call):
    if call.data == "wrong topic":
        return
    game = get_game_by_message(call)
    if not game or not game.get_current_round():
        return
    if call.data.startswith("topic_"):
        if call.from_user.id == game.admin_id:
            topic = call.data[len("topic_"):]
            start_topic_round(game, topic)
            return
    if (game.get_current_round().current_question_index - 1 >= len(game.get_current_round().questions)):
        send_next_question(call.message, game)
        return
    current_question = game.get_current_round().questions[game.get_current_round().current_question_index - 1]
    
    if call.data == "continue":
        if call.from_user.id == game.admin_id:
            if Question.timer_sec:
                Question.timer_sec.cancel()
            if current_question.question_type == "multiple_choice":
                correct_count = sum(1 for answer in current_question.answers.values() if answer == current_question.correct_answer)
                send_message(call.message.chat.id, f"{correct_count} игрок(ов) ответили правильно.")
                send_next_question(call.message, game)
            elif current_question.question_type == "open":
                unique_answers = set(current_question.answers.values())
                markup = types.InlineKeyboardMarkup()
                for answer in unique_answers:
                    markup.add(types.InlineKeyboardButton(text=answer, callback_data=f"correct_{answer}"))
                markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_question"))
                send_message(call.message.chat.id, "Уникальные ответы игроков:", reply_markup=markup) 
            elif current_question.question_type == "big_open":
                unique_answers = set(current_question.answers.values())
                for answer in unique_answers:
                    markup = types.InlineKeyboardMarkup()
                    array = [types.InlineKeyboardButton(text=str(i), callback_data=f"score_{str(i)}_{answer}") for i in range(current_question.max_score)]
                    markup.add(*array)
                    bot.send_message(call.message.chat.id, answer, reply_markup=markup)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_question"))
                send_message(call.message.chat.id,"Дальше", reply_markup=markup)
    elif call.data.startswith("correct_"):
        if call.from_user.id == game.admin_id:
            correct_answer = call.data[len("correct_"):]
            for player_id, answer in current_question.answers.items():
                if answer == correct_answer:
                    game.players[player_id]["score"] += 1
            send_message(call.message.chat.id, f"Ответ '{correct_answer}' отмечен как правильный.")
    elif call.data.startswith("score_"):
        if call.from_user.id == game.admin_id:
            s = call.data[len("score_"):]
            score = s[:s.find('_')]
            answer_score = s[s.find('_')+1:]
            for player_id, answer in current_question.answers.items():
                if answer == answer_score:
                    game.players[player_id]["score"] += int(score)
            bot.delete_message(call.message.chat.id, call.message.message_id)
    elif call.data == "next_question":
        if call.from_user.id == game.admin_id:
            send_next_question(call.message, game)
    elif call.data.startswith("start_"):
        if call.from_user.id == game.admin_id:
            player_id = call.data[len("start_"):]
            game.get_current_round().timer_sec.start()
            game.get_current_round().timer_minute.start()
            send_next_question(call.message, game, player_id)
    elif call.data.startswith("plus_"):
        if call.from_user.id == game.admin_id:
            player_id = call.data[len("plus_"):]
            if game.get_current_round().get_current_question().question_type == "pentagon":
                question = game.get_current_round().get_current_question()
                point = question.get_point(True)
                game.players[int(player_id)]["score"] += point
                bot.delete_message(call.message.chat.id,call.message.message_id)
            else:
                game.players[int(player_id)]["score"] += 1
                send_next_question(call.message, game, player_id)
    elif call.data.startswith("minus_"):
        if call.from_user.id == game.admin_id:
            player_id = call.data[len("minus_"):]
            if game.get_current_round().get_current_question().question_type == "pentagon":
                question = game.get_current_round().get_current_question()
                point = question.get_point(False)
                game.players[int(player_id)]["score"] += point
                bot.delete_message(call.message.chat.id,call.message.message_id)
            else:
                send_next_question(call.message, game, player_id)
    elif call.data.startswith("multianswer_"):
        player_id = call.from_user.id
        if player_id in game.players:
            answer = call.data[len("multianswer_"):]
            current_question.answers[player_id] = answer
            send_message(call.message.chat.id, f"Ваш ответ '{answer}' принят.")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            if current_question.question_type == "multiple_choice" and current_question.check_answer(answer):
                game.players[player_id]["score"] += 1
            send_message(game.admin_id, f"Игрок {game.players[player_id]['name']} ответил: {answer[:100]}")
    elif call.data == "next_hint":
        if call.from_user.id == game.admin_id:
            send_next_hint(call.message, game)
    else:
        return

@bot.message_handler(func=lambda message: True)
def handle_open_question(message):
    game = get_game_by_message(message)
    if game and game.get_current_round():
        if (game.get_current_round().current_question_index - 1 >= len(game.get_current_round().questions)):
            return
        current_question = game.get_current_round().questions[game.get_current_round().current_question_index - 1]
        add_message(message.chat.id, message.message_id)
        if current_question.question_type == "open" or current_question.question_type == "big_open":
            current_question.answers[message.from_user.id] = message.text
            msg = send_message(message.chat.id, f"Ваш ответ {message.text} принят.")
            bot.delete_message(message.chat.id, msg.message_id - 1)
            send_message(game.admin_id, f"Игрок {game.players[message.from_user.id]['name']} ответил: {message.text}")
        if current_question.question_type == "pentagon":
            current_question.answers[message.from_user.id] = message.text
            msg = send_message(message.chat.id, f"Ваш ответ {message.text} принят.")
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="-", callback_data=f"minus_{message.from_user.id}"),
                       types.InlineKeyboardButton(text="+", callback_data=f"plus_{message.from_user.id}"))
            bot.delete_message(message.chat.id, msg.message_id - 1)
            send_message(game.admin_id, f"Игрок {game.players[message.from_user.id]['name']} ответил: {message.text}", reply_markup=markup)

