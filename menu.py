from telebot import types

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_start_game = types.KeyboardButton('/create_game')
    btn_join_game = types.KeyboardButton('/join_game')
    btn_start_round = types.KeyboardButton('/start_round')
    btn_end_round = types.KeyboardButton('/end_round')
    markup.add(btn_start_game, btn_join_game, btn_start_round, btn_end_round)
    return markup

