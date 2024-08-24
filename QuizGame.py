class QuizGame:
    def __init__(self, admin_id, game_name):
        self.admin_id = admin_id
        self.game_name = game_name
        self.players = {}
        self.rounds = []
        self.current_round = None

    def add_player(self, player_id, player_name):
        self.players[player_id] = {"name": player_name, "score": 0}