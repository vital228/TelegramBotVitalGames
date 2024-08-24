from telebot import types
from get_game_by import get_game_by_admin
from process_join_game import process_join_game
from bots import bot, games
from Round import Round
from Question import load_questions_from_file, Question
from QuizGame import QuizGame
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
        bot.send_message(message.chat.id, "Введите описание правил для нового раунда", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_round_rules, game)

@bot.message_handler(commands=["end_round"])
def end_round(message):
    game = get_game_by_admin(message)
    if game and game.current_round:
        leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in game.players.items()])
        bot.send_message(message.chat.id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        game.current_round = None

def set_game_name(message):
    game_name = message.text
    if game_name not in games:
        games[game_name] = QuizGame(admin_id=message.from_user.id, game_name=game_name)
        bot.send_message(message.chat.id, f"Игра '{game_name}' создана. Игроки могут присоединиться командой /join_game", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем уже существует. Введите другое имя.", reply_markup=main_menu())

def set_round_rules(message, game):
    round_name = f"Раунд {len(game.rounds) + 1}"
    game.current_round = Round(name=round_name, rules=message.text)
    game.rounds.append(game.current_round)
    questions = load_questions_from_file('questions.json')
    game.current_round.load_questions(questions)
    bot.send_message(message.chat.id, f"{round_name} начался. Вопросы загружены.", reply_markup=main_menu())
    for player_id in game.players:
        bot.send_message(player_id, f"Начался {round_name}. Правила: {game.current_round.rules}")
    send_next_question(message, game)
