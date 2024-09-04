import json
class Question:
    timer_sec = None

    def __init__(self, text, question_type, correct_answer=None, options=None, photo=None,
                  audio = None, second = None, max_score = None, url_photo=None, url_audio=None):
        self.text = text
        self.question_type = question_type
        self.correct_answer = correct_answer
        self.options = options
        self.answers = {}
        self.photo = photo
        self.audio = audio
        self.second = second
        self.max_score = max_score
        self.url_photo = url_photo
        self.url_audio = url_audio

    def check_answer(self, answer):
        if self.question_type == "multiple_choice":
            return answer.strip().lower() == self.correct_answer.strip().lower()
        elif self.question_type == "open":
            return answer.strip().lower() == self.correct_answer.strip().lower()
        
def load_questions_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    questions = []
    for item in data:
        if item['type'] == 'pentagon':
            question = PentagonQuestion(
                text=item['text'],
                question_type=item['type'],
                correct_answer=item['correct_answer'],
                options=item.get('options', None),
                photo = item.get('photo', None),
                audio = item.get('audio', None),
                second = item.get('second', 15),
                max_score = item.get('max_score', None),
                url_audio= item.get('url_audio', None),
                url_photo= item.get('url_photo', None)
            )
            for hint in item['hints']:
                question.add_hint(hint)
        else:
            question = Question(
                text=item['text'],
                question_type=item['type'],
                correct_answer=item['correct_answer'],
                options=item.get('options', None),
                photo = item.get('photo', None),
                audio = item.get('audio', None),
                second = item.get('second', 15),
                max_score = item.get('max_score', None),
                url_audio= item.get('url_audio', None),
                url_photo= item.get('url_photo', None)
            )
        questions.append(question)
    return questions

class PentagonQuestion(Question):
    def __init__(self, text, question_type, max_score = 5, correct_answer=None, options=None, photo=None,
                  audio = None, second = None, url_photo=None, url_audio=None):
        self.text = text
        self.question_type = question_type
        self.correct_answer = correct_answer
        self.options = options
        self.answers = {}
        self.photo = photo
        self.audio = audio
        self.second = second
        self.max_score = max_score
        self.url_photo = url_photo
        self.url_audio = url_audio
        self.hints = []
        self.hint_index = 0

    def add_hint(self, text):
        self.hints.append(text)
    
    def next_hint(self):
        if (self.hint_index<len(self.hints)):
            hint = self.hints[self.hint_index]
            self.hint_index += 1
            return hint
        return None
    
    def current_hint(self):
        if (self.hint_index<=len(self.hints) and self.hint_index>0):
            return self.hints[self.hint_index]
        if self.hint_index == 0:
            return self.text
        return None
        
    def get_point(self, is_right):
        if is_right:
            return self.max_score - self.hint_index
        else:
            return self.hint_index - self.max_score + 1


