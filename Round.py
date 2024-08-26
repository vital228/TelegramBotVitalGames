import json
from Question import load_questions_from_file
class Round:
    def __init__(self, name, rules, round_type):
        self.name = name
        self.rules = rules
        self.type = round_type
        self.questions = []
        self.topics = []
        self.scores = {}
        self.current_question_index = 0

    def load_questions(self, questions):
        self.questions = questions

    def add_topics(self, topic):
        round = Round(topic, "Отвечаете на вопросы у вас 60 секунд", "topic")
        round.load_questions(f'game_1/{topic}.json')
        self.topics.append({"round": round,
                            "is_played": False})


    def get_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None
 

def load_round_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    rounds = []
    for item in data:
        round = Round(
            name=item['name_round'],
            round_type=item['type_round'],
            rules=item['rules'],
        )
        if round.type == 'simple':
            round.load_questions(load_questions_from_file(item['file_questions']))
        else:
            for topic in item['topics']:
                round.add_topics(topic)
        rounds.append(round)
    return rounds