class QuizGame:
    def __init__(self, admin_id, game_name):
        self.admin_id = admin_id
        self.game_name = game_name
        self.players = {}
        self.rounds = []
        self.current_round_index = 0

    def add_player(self, player_id, player_name):
        self.players[player_id] = {"name": player_name, "score": 0}

    def get_next_round(self):
        if self.current_round_index < len(self.rounds):
            round = self.rounds[self.current_round_index]
            self.current_round_index += 1
            return round
        return None
    def get_current_round(self):
        if self.current_round_index < len(self.rounds):
            return self.rounds[self.current_round_index - 1]
        return None
    
def sorted_score(game):
    return {key: value for key, 
               value in sorted(game.players.items(), 
                               key=lambda item: item[1]['score'])}