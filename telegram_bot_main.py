import telebot
from telebot import types
import json
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

games = {}

class QuizGame:
    def __init__(self, admin_id, game_name):
        self.admin_id = admin_id
        self.game_name = game_name
        self.players = {}
        self.rounds = []
        self.current_round = None

    def add_player(self, player_id, player_name):
        self.players[player_id] = {"name": player_name, "score": 0}

class Round:
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules
        self.questions = []
        self.scores = {}
        self.current_question_index = 0

    def load_questions(self, questions):
        self.questions = questions

    def get_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None

class Question:
    def __init__(self, text, question_type, correct_answer=None, options=None):
        self.text = text
        self.question_type = question_type
        self.correct_answer = correct_answer
        self.options = options
        self.answers = {}

    def check_answer(self, answer):
        if self.question_type == "multiple_choice":
            return answer.strip().lower() == self.correct_answer.strip().lower()
        elif self.question_type == "open":
            return answer.strip().lower() == self.correct_answer.strip().lower()

def load_questions_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    questions = []
    for item in data:
        question = Question(
            text=item['text'],
            question_type=item['type'],
            correct_answer=item['correct_answer'],
            options=item.get('options', None)
        )
        questions.append(question)
    return questions

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start_game = types.KeyboardButton('/create_game')
    btn_join_game = types.KeyboardButton('/join_game')
    btn_start_round = types.KeyboardButton('/start_round')
    btn_end_round = types.KeyboardButton('/end_round')
    markup.add(btn_start_game, btn_join_game, btn_start_round, btn_end_round)
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать в Квиз Бот! Вы можете выбрать одну из команд ниже.", reply_markup=main_menu())

@bot.message_handler(commands=["create_game"])
def create_game(message):
    bot.send_message(message.chat.id, "Введите имя для новой игры", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, set_game_name)

def set_game_name(message):
    game_name = message.text
    if game_name not in games:
        games[game_name] = QuizGame(admin_id=message.from_user.id, game_name=game_name)
        bot.send_message(message.chat.id, f"Игра '{game_name}' создана. Игроки могут присоединиться командой /join_game", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем уже существует. Введите другое имя.", reply_markup=main_menu())

@bot.message_handler(commands=["join_game"])
def join_game(message):
    bot.send_message(message.chat.id, "Введите имя игры, к которой хотите присоединиться", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_join_game)

def process_join_game(message):
    game_name = message.text
    if game_name in games:
        game = games[game_name]
        if message.from_user.id not in game.players:
            game.add_player(message.from_user.id, message.from_user.full_name)
            bot.send_message(game.admin_id, f"Игрок {message.from_user.full_name} присоединился к игре.")
            bot.send_message(message.chat.id, f"Вы присоединились к игре '{game_name}'", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "Вы уже присоединились к этой игре", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем не найдена", reply_markup=main_menu())

@bot.message_handler(commands=["start_round"])
def start_round(message):
    game = get_game_by_admin(message)
    if game:
        bot.send_message(message.chat.id, "Введите описание правил для нового раунда", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, set_round_rules, game)

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

@bot.message_handler(commands=["end_round"])
def end_round(message):
    game = get_game_by_admin(message)
    if game and game.current_round:
        leaderboard = "\n".join([f"{game.players[p_id]['name']}: {player['score']}" for p_id, player in game.players.items()])
        bot.send_message(message.chat.id, f"Раунд завершен. Таблица лидеров:\n{leaderboard}", reply_markup=main_menu())
        game.current_round = None

def get_game_by_admin(message):
    for game in games.values():
        if game.admin_id == message.from_user.id:
            return game
    return None

def get_game_by_message(message):
    user_id = message.from_user.id if hasattr(message, 'from_user') else message.chat.id
    for game in games.values():
        if user_id in [game.admin_id] + list(game.players.keys()):
            return game
    return None

if __name__ == "__main__":
    bot.polling(none_stop=True)