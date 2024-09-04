import sqlite3
from QuizGame import QuizGame
from Round import load_round_from_file

def start():
    conn = sqlite3.connect('VitalGamesBotDB.db')
    cur = conn.cursor()

    # Таблица для хранения информации об играх
    cur.execute('''CREATE TABLE IF NOT EXISTS games (
                    game_name TEXT PRIMARY KEY, 
                    admin_id INTEGER, 
                    round_number INTEGER)''')

    # Таблица для хранения информации об игроках в играх
    cur.execute('''CREATE TABLE IF NOT EXISTS users_in_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    game_name TEXT, 
                    player_id INTEGER, 
                    player_name TEXT, 
                    score INTEGER, 
                    FOREIGN KEY(game_name) REFERENCES games(game_name))''')

    conn.commit()
    conn.close()

def update_info(game: QuizGame):
    conn = sqlite3.connect('VitalGamesBotDB.db')
    cur = conn.cursor()

    # Обновляем или вставляем информацию об игре
    cur.execute('''INSERT OR REPLACE INTO games (game_name, admin_id, round_number) 
                   VALUES (?, ?, ?)''', (game.game_name, game.admin_id, game.current_round_index))
    
    # Обновляем или вставляем информацию об игроках
    for player_id, player_info in game.players.items():
        cur.execute('''INSERT OR REPLACE INTO users_in_games (game_name, player_id, player_name, score) 
                       VALUES (?, ?, ?, ?)''', 
                    (game.game_name, player_id, player_info['name'], player_info['score']))
    
    conn.commit()
    conn.close()

def delete(game_name: str):
    conn = sqlite3.connect('VitalGamesBotDB.db')
    cur = conn.cursor()

    # Удаляем все записи об игроках, связанных с игрой
    cur.execute('DELETE FROM users_in_games WHERE game_name = ?', (game_name,))
    
    # Удаляем запись об игре
    cur.execute('DELETE FROM games WHERE game_name = ?', (game_name,))
    
    conn.commit()
    conn.close()

def get_all_games():
    conn = sqlite3.connect('VitalGamesBotDB.db')
    cur = conn.cursor()

    # Инициализируем пустой словарь игр
    games = {}

    # Получаем все игры из таблицы games
    cur.execute('SELECT * FROM games')
    games_data = cur.fetchall()

    # Заполняем словарь games данными из базы
    for game_row in games_data:
        game_name = game_row[0]
        admin_id = game_row[1]
        round_number = game_row[2]

        # Создаем экземпляр QuizGame
        game = QuizGame(admin_id, game_name)
        game.current_round_index = round_number

        # Получаем всех игроков, участвующих в этой игре
        cur.execute('SELECT player_id, player_name, score FROM users_in_games WHERE game_name = ?', (game_name,))
        players_data = cur.fetchall()

        for player_row in players_data:
            player_id = player_row[0]
            player_name = player_row[1]
            score = player_row[2]

            # Добавляем игрока в игру
            game.add_player(player_id, player_name)
            game.players[player_id]['score'] = score

        # Добавляем игру в словарь games
        games[game_name] = game
        games[game_name].rounds = load_round_from_file('game_1/rounds.json')

    conn.close()
    return games