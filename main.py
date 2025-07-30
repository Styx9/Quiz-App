import html
import sys
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,QComboBox, QStackedWidget
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget,QSpinBox


def parsing_json(data):
    questions = []
    for q in data["results"]:
        question = {
            "question": html.unescape(q["question"]),
            "options": [html.unescape(q["correct_answer"])] + [html.unescape(x) for x in q["incorrect_answers"]],
            "correct_answer": html.unescape(q["correct_answer"])
        }
        questions.append(question)  # This line was missing
    return questions

class StartPage(QWidget):
    def __init__(self,start_callback):
        super().__init__()
        self.start_callback = start_callback
        layout = QVBoxLayout(self)

        logo = QLabel()
        pixmap = QPixmap("icon.png")
        scaled_pixmap = pixmap.scaled(
            QSize(300, 300),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(scaled_pixmap)
        layout.addWidget(logo)
        self.welcome_label = QLabel("Welcome to the Quiz App")
        self.welcome_label.setObjectName("welcomeLabel")
        layout.addWidget(self.welcome_label)

        self.difficulty_label = QLabel("Select Difficulty")
        self.combo_box = QComboBox()
        self.combo_box.addItems(["easy", "medium", "hard"])
        layout.addWidget(self.difficulty_label)
        layout.addWidget(self.combo_box)
        self.label_dif = QLabel("Number of Questions:")
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 50)
        layout.addWidget(self.label_dif)
        layout.addWidget(self.spin_box)
        self.button = QPushButton("Start")
        self.button.clicked.connect(self.start_quiz)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def start_quiz(self):
        num_questions = self.spin_box.value()
        difficulty = self.combo_box.currentText()
        self.start_callback(difficulty,num_questions)

class QuizPage(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Quiz Page")
            #self.resize(400, 300)
            self.question_index = 0
            self.score = 0
            self.questions = []  # Initialize questions list
            self.layout = QVBoxLayout(self)
            self.question_label = QLabel("Question")
            self.question_label.setWordWrap(True)
            self.question_label.setMinimumHeight(100)
            self.layout.addWidget(self.question_label)
            self.option_buttons = [QPushButton() for _ in range(4)]
            for btn in self.option_buttons:
                btn.clicked.connect(self.check_answer)
                self.layout.addWidget(btn)

        def load_questions(self, questions):
            self.questions = questions
            self.question_index = 0
            self.score = 0
            if self.questions:
                self.show_question()
            else:
                self.end_quiz()

        def show_question(self):
            if self.question_index < len(self.questions):
                q = self.questions[self.question_index]
                self.question_label.setText(f"Q{self.question_index + 1}. {q['question']}")
                for i, option in enumerate(q["options"]):
                    self.option_buttons[i].setText(str(option))  # Convert to string
                    self.option_buttons[i].show()
            else:
                self.end_quiz()

        def check_answer(self):
            sender = self.sender()
            if sender and self.question_index < len(self.questions):
                selected_answer = sender.property("text")
                correct_answer = self.questions[self.question_index]["correct_answer"]
                if selected_answer == correct_answer:
                    self.score += 1
                self.question_index += 1
                self.show_question()

        def end_quiz(self):
            self.question_label.setText(f"Quiz Finished.\nYour score is {self.score}/{len(self.questions)}")
            for btn in self.option_buttons:
                btn.hide()

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.setWindowTitle("Quiz App")
        self.resize(500,400)
        self.stack = QStackedWidget()
        self.start_page = StartPage(self.start_quiz)
        self.quiz_page = QuizPage()
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.quiz_page)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

    def start_quiz(self, difficulty,num_questions):
        try:
            response = requests.get(f"https://opentdb.com/api.php?amount={num_questions}&difficulty={difficulty}&type=multiple")
            response.raise_for_status()
            data = response.json()
            self.questions = parsing_json(data)
            self.quiz_page.load_questions(self.questions)
            self.stack.setCurrentWidget(self.quiz_page)
        except Exception as e:
            print(f"Error loading questions: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = QuizApp()
    window.show()
    sys.exit(app.exec())