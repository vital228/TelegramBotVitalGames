from bots import bot, games
from menu import main_menu

def process_join_game(message):
    game_name = message.text
    if game_name in games.keys():
        game = games[game_name]
        if message.from_user.id not in game.players:
            game.add_player(message.from_user.id, message.from_user.full_name)
            bot.send_message(game.admin_id, f"Игрок {message.from_user.full_name} присоединился к игре.")
            bot.send_message(message.chat.id, f"Вы присоединились к игре '{game_name}'", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "Вы уже присоединились к этой игре", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Игра с таким именем не найдена", reply_markup=main_menu())
