import threading
from flask import Flask, render_template, request, jsonify, json
import webview
import mathsQuiz


class App:
    def __init__(self):
        # Create Flask instance
        self.app = Flask(__name__)

        # Session Data:
        self.currentManager: mathsQuiz.QuestionManager | None = None
        self.history = {}

        # Register app menus
        self.appMenus()
        self.appAPI()

        # Start Flask as a background task (Very important, Android has strict memory management)
        self.flaskServer = threading.Thread(target=self.runFlask, daemon=True)
        self.flaskServer.start()

        # Launch the pywebview window container in the main thread
        self.window = webview.create_window('Maths Quiz', 'http://127.0.0.1:5000/')
        self.runWindow()

    # Run window
    def runWindow(self):
        webview.start()

    # Launch flask server.
    def runFlask(self):
        self.app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False,threaded=True)


    def appMenus(self):
        # Now self.app safely exists and can be targeted by decorators
        @self.app.route('/')
        def index():
            if self.currentManager is not None:
                if self.currentManager.activeTimer is not None:
                    self.currentManager.activeTimer.cancel()
                self.currentManager = None
            return render_template("index.html")

        @self.app.route('/level-selector')
        def levelSelector():
            print("Level selector menu opened")
            questionType = request.args.get('question-type')
            print(f"Level Selector for Question Type: {questionType}")

            return render_template(
                'levelSelector.html',
                questionType=questionType
            )

        @self.app.route('/question')
        def question():

            def results():

                score = 0
                for question in self.currentManager.questions:
                    if question.answer == question.userAnswer:
                        score += 1

                return render_template(
                    'results.html',
                    questionList=self.currentManager.questions,
                    score=score
                )

            print("Question menu opened")
            questionType = request.args.get('question-type')
            level = request.args.get('level')
            state = request.args.get('state')
            print(f"Question Type: {questionType}, Level: {level}")

            type = ""
            if questionType == "addition":
                type = "+"
            elif questionType == "subtraction":
                type = "-"
            elif questionType == "multiplication":
                type = "*"
            elif questionType == "division":
                type = "/"
            elif questionType == "mix":
                type = "mix"
            else: raise ValueError("Invalid question type")

            question = None
            if state == "new":
                self.currentManager = mathsQuiz.QuestionManager(10)
                question = self.currentManager.genQuestion(type, int(level))
                print(f"Questions List Length: {len(self.currentManager.questions)}")
            elif state == "current":
                question = self.currentManager.genQuestion(type, int(level))

            if question is None: return results()

            return render_template(
                'question.html',
                question=question,
                questionType=questionType,
                level=level,
                count=len(self.currentManager.questions)
            )

        @self.app.route('/history')
        def history():
            import mathCommon as mc

            history = mc.getHistory()

            return render_template(
                'history.html',
                history=history,
            )

    def appAPI(self):

        @self.app.route("/api/submit-answer", methods=["POST"])
        def submitAnswer():
            print("Got request to submit answer")


            data = request.get_json()
            answer = data["answer"]

            questionIndex = len(self.currentManager.questions) - 1
            question = self.currentManager.questions[questionIndex]

            result = question.checkAnswer(answer, self.currentManager.timeLimitPassed)

            if result:
                if not self.currentManager.timeLimitPassed:
                    self.currentManager.updateDifficulty(int(answer))
                self.currentManager.saveToHistory()
                if self.currentManager.activeTimer is not None:
                    self.currentManager.activeTimer.cancel()
                return jsonify({"status": "success", "message": "Answer submitted successfully"})

            return jsonify({"status": "error", "message": "Answer submitted unsuccessfully"})



