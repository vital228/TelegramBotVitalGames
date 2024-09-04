import json
from Question import load_questions_from_file
from queue import Queue
class Round:
    def __init__(self, name, rules, round_type, max_player = None):
        self.name = name
        self.rules = rules
        self.type = round_type
        self.questions = []
        self.topics = []
        self.scores = {}
        self.timer_minute = None
        self.queue_players = Queue()
        self.current_question_index = 0
        self.cancel_timer = False
        self.max_player = max_player

    def load_questions(self, questions):
        self.questions = questions

    def add_topics(self, topic):
        self.topics.append({"round": topic,
                            "is_played": False})


    def get_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None
    
    def get_current_question(self):
        if self.current_question_index <= len(self.questions) and self.current_question_index>0:
            return self.questions[self.current_question_index - 1]
        return None
 

def load_round_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    rounds = []
    for item in data:
        round = Round(
            name=item['name_round'],
            round_type=item['type_round'],
            rules=item['rules'],
            max_player=item.get('max_player', None)
        )
        if round.type == 'simple':
            round.load_questions(load_questions_from_file(item['file_questions']))
        else:
            for topic in item['topics']:
                round.add_topics(topic)
        rounds.append(round)
    return rounds