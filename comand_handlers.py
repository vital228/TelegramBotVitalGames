from telebot import types
from get_game_by import get_game_by_admin
from process_join_game import process_join_game
from bots import bot, games
from Round import Round, load_round_from_file
from Question import load_questions_from_file, Question
from QuizGame import QuizGame, sorted_score
from send_next_question import send_next_question
from menu import main_menu

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в Квиз Бот! Вы можете выбрать одну из команд ниже.", reply_markup=main_menu())

@bot.message_handler(commands=["create_game"])
def create_game(message):
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
        round = game.get_next_round()
        if round:
            for player_id in game.players:
                bot.send_message(player_id, f"Начался {round.name}. Правила: {round.rules}")
            markup = types.InlineKeyboardMarkup()
            if round.type == 'simple':
                markup.add(types.InlineKeyboardButton(text="Продолжить", callback_data="next_question"))
                bot.send_message(message.chat.id, f"{round.name} начался. Вопросы загружены.", reply_markup=markup)
            if round.type == 'topics':
                for topic in round.topics:
                    if topic['is_played']:
                        markup.add(types.InlineKeyboardButton(text=f"{topic['round']} ❌", callback_data="wrong topic"))
                    else:
                        markup.add(types.InlineKeyboardButton(text=f"{topic['round']}", callback_data=f"topic_{topic['round']}"))
        else:
            leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in sorted_score(game).items()
 ])
            bot.send_message(message.chat.id, f"Раундов больше нет. Финальная таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        for player_id in game.players:
            bot.send_message(player_id, f"Раундов больше нет. Финальная таблица лидеров:\n{leaderboard}", reply_markup=main_menu())

@bot.message_handler(commands=["end_round"])
def end_round(message):
    game = get_game_by_admin(message)
    if game and game.get_current_round():
        leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in sorted_score(game).items()
 ])
        bot.send_message(message.chat.id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        for player_id in game.players:
            bot.send_message(player_id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        game.current_round = None

def set_game_name(message):
    game_name = message.text
    if game_name not in games:
        games[game_name] = QuizGame(admin_id=message.from_user.id, game_name=game_name)
        games[game_name].rounds = load_round_from_file('game_1/rounds.json')
        bot.send_message(message.chat.id, f"Игра '{game_name}' создана. Игроки могут присоединиться командой /join_game", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем уже существует. Введите другое имя.", reply_markup=main_menu())

