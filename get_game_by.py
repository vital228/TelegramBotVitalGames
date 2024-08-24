from bots import games
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