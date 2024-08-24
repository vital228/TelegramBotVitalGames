import json
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