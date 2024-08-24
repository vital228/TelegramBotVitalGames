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