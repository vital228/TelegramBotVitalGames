import tkinter as tk
from tkinter import messagebox
import json

class QuestionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сохранение вопросов в JSON")

        # Поле для ввода названия файла
        self.filename_label = tk.Label(root, text="Название файла:")
        self.filename_label.pack()

        self.filename_entry = tk.Entry(root, width=50)
        self.filename_entry.pack()

        # Поле для ввода вопроса
        self.question_label = tk.Label(root, text="Вопрос:")
        self.question_label.pack()

        # Рамка для размещения поля ввода и кнопки вставки
        self.question_frame = tk.Frame(root)
        self.question_frame.pack()

        self.question_entry = tk.Entry(self.question_frame, width=50)
        self.question_entry.pack(side=tk.LEFT)

        # Кнопка для вставки текста из буфера обмена
        self.paste_button = tk.Button(self.question_frame, text="Вставить из буфера обмена", command=self.paste_from_clipboard)
        self.paste_button.pack(side=tk.LEFT)

        # Привязка события Ctrl+V к полю ввода вопроса
        self.question_entry.bind('<Control-v>', self.handle_paste)

        # Поле для ввода ответа
        self.answer_label = tk.Label(root, text="Ответ:")
        self.answer_label.pack()

        self.answer_entry = tk.Entry(root, width=50)
        self.answer_entry.pack()

        # Кнопка для добавления вопроса
        self.add_button = tk.Button(root, text="Добавить вопрос", command=self.add_question)
        self.add_button.pack()

        # Кнопка для сохранения в JSON
        self.save_button = tk.Button(root, text="Сохранить в JSON", command=self.save_to_json)
        self.save_button.pack()

        # Список для хранения вопросов
        self.questions = []

    def paste_from_clipboard(self):
        # Вставляем текст из буфера обмена в поле для ввода вопроса
        clipboard_text = self.root.clipboard_get()
        self.question_entry.delete(0, tk.END)
        self.question_entry.insert(0, clipboard_text)

    def handle_paste(self, event):
        # Обработка сочетания клавиш Ctrl+V
        self.paste_from_clipboard()
        return "break"  # Предотвращаем дальнейшую обработку события по умолчанию

    def add_question(self):
        question = self.question_entry.get()
        answer = self.answer_entry.get()

        if question and answer:
            self.questions.append({
                "text": question,
                "type": "open_topic",
                "correct_answer": answer
            })
            messagebox.showinfo("Добавлено", "Вопрос добавлен.")
            self.question_entry.delete(0, tk.END)
            self.answer_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Пожалуйста, введите вопрос и ответ.")

    def save_to_json(self):
        filename = self.filename_entry.get()
        if not filename.endswith(".json"):
            filename += ".json"

        if self.questions:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранено", f"Вопросы сохранены в файл {filename}.")
            self.questions = []
            self.filename_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Сначала добавьте вопросы.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionApp(root)
    root.mainloop()
