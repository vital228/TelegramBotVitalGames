from telebot import types
from get_game_by import get_game_by_admin
from process_join_game import process_join_game
from bots import bot, games, delete_all_message, send_message
from Round import Round, load_round_from_file
from Question import load_questions_from_file, Question
from QuizGame import QuizGame, sorted_score
from send_next_question import send_next_question
from menu import main_menu
from topics_round import start_topic_round
from DataBase import update_info, delete

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в Квиз Бот! Вы можете выбрать одну из команд ниже.", reply_markup=main_menu())

@bot.message_handler(commands=["create_game"])
def create_game(message):
    if get_game_by_admin(message):
        bot.send_message(message.chat.id, "У вас есть не законченная игра.", reply_markup=main_menu())
        return
    bot.send_message(message.chat.id, "Введите имя для новой игры", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, set_game_name)

@bot.message_handler(commands=["join_game"])
def join_game(message):
    bot.send_message(message.chat.id, "Введите имя игры, к которой хотите присоединиться", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_join_game)

@bot.message_handler(commands=["start_round"])
def start_round(message):
    game = get_game_by_admin(message)
    if game:
        if (game.get_current_round()) and (game.get_current_round().type == "topics") and (any(not it['is_played'] for it in game.get_current_round().topics)):
            round = game.get_current_round()
        else:
            round = game.get_next_round()
        if round:
            players = get_top_n_players(game.players, round.max_player)
            game.players.clear()
            for player_id, player in players:
                game.players[player_id] = player
            for player_id in game.players:
                send_message(player_id, f"Начался {round.name}. Правила: {round.rules}")
            markup = types.InlineKeyboardMarkup()
            if round.type == 'simple':
                markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_question"))
                send_message(message.chat.id, f"{round.name} начался. Вопросы загружены.", reply_markup=markup)
            if round.type == 'topics':
                if (all(not it['is_played'] for it in round.topics)):
                    for p_id, player in sorted_score(game).items():
                        round.queue_players.put(p_id)
                text_topics = ""
                for topic in round.topics:
                    if topic['is_played']:
                        markup.add(types.InlineKeyboardButton(text=f"{topic['round']} ❌", callback_data="wrong topic"))
                        text_topics+=f"|{topic['round']} ❌|"
                    else:
                        markup.add(types.InlineKeyboardButton(text=f"{topic['round']}", callback_data=f"topic_{topic['round']}"))
                        text_topics+=f"|{topic['round']}|"
                send_message(game.admin_id, f"Игрок: {bot.get_chat(round.queue_players.queue[0]).first_name} {bot.get_chat(round.queue_players.queue[0]).last_name}", reply_markup=markup)
                send_message(round.queue_players.queue[0], text_topics)
        else:
            leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in sorted_score(game).items()
 ])
            bot.send_message(message.chat.id, f"Раундов больше нет. Финальная таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
            for player_id in game.players:
                bot.send_message(player_id, f"Раундов больше нет. Финальная таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
            delete(game.game_name)
            del(games[game.game_name])
@bot.message_handler(commands=["end_round"])
def end_round(message):
    game = get_game_by_admin(message)
    if game and game.get_current_round():
        delete_all_message()
        leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in sorted_score(game).items()
 ])
        send_message(message.chat.id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        for player_id in game.players:
            send_message(player_id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        update_info(game)

def set_game_name(message):
    game_name = message.text
    if game_name not in games:
        games[game_name] = QuizGame(admin_id=message.from_user.id, game_name=game_name)
        games[game_name].rounds = load_round_from_file('game_1/rounds.json')
        bot.send_message(message.chat.id, f"Игра '{game_name}' создана. Игроки могут присоединиться командой /join_game", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем уже существует. Введите другое имя.", reply_markup=main_menu())

def get_top_n_players(players, N):

    # Сортируем игроков по очкам в порядке убывания и берем первые N записей
    if not N:
        return players
    top_n_players = sorted(players.items(), 
                               key=lambda item: item[1]['score'], reverse=True)[:N]
    return top_n_players