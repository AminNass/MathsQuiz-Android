import threading
from flask import Flask, render_template, request, jsonify
import webview
import androidSound
import mathsQuiz
import queue
import time

class App:
    def __init__(self):
        # Create Flask instance.
        self.app = Flask(__name__)

        # Create question manager as an object in this class.
        # The manager allows for generation of questions with the maximum of 10.
        # For every instance is a set of 10 questions.
        self.currentManager: mathsQuiz.QuestionManager | None = None

        # These are for android specific features.
        # While they are quite unstable this allows for audio playing in android.
        # The instability is caused by calling it via python on different threads.
        # The problem is python has their own thread, and the flask server is its own thread.
        # This is required as android wouldn't allow for both the flask server and pywebview to be on the same thread.
        self.AndroidMediaPlayer = androidSound.AndroidMediaPlayer
        self.AndroidSoundPool = androidSound.AndroidSoundPool

        # These will initialize the main menus and apis.
        self.appMenus()
        self.appAPI()

        # This will put the flask server on a different thread and start it.
        self.flaskServer = threading.Thread(target=self.runFlask, daemon=True)
        self.flaskServer.start()

        # To prevent the program from crashing I made a queue that prevents python from calling the android sound pool,
        # multiple times at once. I set the queue size to 15 to prevent overload. Sometimes It's still unstable.
        self.soundQueue = queue.Queue(maxsize=15)
        # This preloads sounds into the sound pool to allow for fast playing.
        # All frequently played sound are loaded in here to prevent the app from freezing up.
        self.AndroidSoundPool.preload('click', 'click.wav')

        # Creates and Launches the pywebview window container in the main thread.
        # Technically on the python thread but its required.
        self.window = webview.create_window('Maths Quiz', 'http://127.0.0.1:5000/')
        self.runWindow()

    # Safe processing of sound. This is what calls the android sound pool.

    def _process_sounds(self):
        try:
            while True:
                key = self.soundQueue.get_nowait()
                self.AndroidSoundPool.play(key)
        except queue.Empty:
            pass

    # A ticking system for the sound pool. Prevents spam clicks. Each sound must be sent every 0.02 seconds.

    def _loop(self):
        while True:
            self._process_sounds()
            time.sleep(0.02)

    # Runs the window and starts the loop on a new thread to prevent the program from slowing down.
    def runWindow(self):
        threading.Thread(target=self._loop, daemon=True).start()
        webview.start()

    # Launch flask server, threaded is set too false to improve stability but has a performance impact.
    def runFlask(self):
        self.app.run(host='0.0.0.0', port=5000, debug=False,use_reloader=False,threaded=False)

    # Functions that declared all the menus in the app.
    def appMenus(self):
        # Home page:
        @self.app.route('/')
        def index():
            # Checks if the current manager is not None, this allows for clearing the current manager after use.
            if self.currentManager is not None:
                # Checks if there is any timers active, if so then it will cancel it.
                if self.currentManager.activeTimer is not None:
                    self.currentManager.activeTimer.cancel()
                self.currentManager = None
            # Simply renders the index HTML template.
            return render_template("index.html")

        # Level selector menu.
        @self.app.route('/level-selector')
        def levelSelector():
            # Gets the question type. This is found on the url eg: '/level-selector?questionType=addition'
            print("Level selector menu opened")
            questionType = request.args.get('question-type')
            print(f"Level Selector for Question Type: {questionType}")

            # Renders the template passing through the question type.
            return render_template(
                'levelSelector.html',
                questionType=questionType
            )

        # Questions Page:
        @self.app.route('/question')
        def question():

            # Function that opens the results page when all the questions are finished.
            def results():
                # Declare the score variable
                score = 0
                # Loop through every single question and add every right answer to the score.
                for question in self.currentManager.questions:
                    if question.answer == question.userAnswer:
                        score += 1

                # Render the template passing through the list of questions and the score.
                return render_template(
                    'results.html',
                    questionList=self.currentManager.questions,
                    score=score
                )

            print("Question menu opened")
            # Gets the arguments for the question type, level and state.
            questionType = request.args.get('question-type')
            level = request.args.get('level')
            state = request.args.get('state')
            print(f"Question Type: {questionType}, Level: {level}")

            # Sets the type to something the question manager can understand.
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

            # Check if the state is current or new:
            question = None
            if state == "new":
                # If the state is new then a new current manager will be loaded.
                self.currentManager = mathsQuiz.QuestionManager(10)
                question = self.currentManager.genQuestion(type, int(level))
                print(f"Questions List Length: {len(self.currentManager.questions)}")
            elif state == "current":
                # If it's the current manager then it will generate a new question.
                question = self.currentManager.genQuestion(type, int(level))

            # Checks if the question is None as when generating a question in the question manager that;
            # has reached the maximum amount of questions generated it will return None calling the results page.
            if question is None: return results()

            # Renders the template passing through the question, the question type, the level (Determines the time limit),
            # and the amount of question in the question (Since it determines what question is the user on).
            return render_template(
                'question.html',
                question=question,
                questionType=questionType,
                level=level,
                count=len(self.currentManager.questions)
            )

        # History page.
        @self.app.route('/history')
        def history():
            import mathCommon as mc

            # Gets the history using the getHistory function.
            history = mc.getHistory()

            # Renders the HTML passing through the question history.
            return render_template(
                'history.html',
                history=history,
            )

    # API:
    def appAPI(self):

        # This functions plays a sound through the android media player.
        @self.app.route('/api/play/<filename>')
        def playSound(filename):
            # The android media player is more stable only because it doesn't get spammed.
            # This calls the media player to play a sound using the file name (Containing the location).
            self.AndroidMediaPlayer.playSound(filename)
            return jsonify({"status": "played"})

        # This function handles sound effects sending through tne android sound pool.
        @self.app.route('/api/sfx/<key>')
        def playSfx(key):
            # This tries to add it to the sound pool queue.
            # This is to prevent overload. If full then it will just be ignored.
            try:
                self.soundQueue.put_nowait(key)
            except queue.Full:
                pass
            return jsonify({"status": "played"})

        # This function handles answer submission.
        @self.app.route("/api/submit-answer", methods=["POST"])
        def submitAnswer():
            print("Got request to submit answer")

            # Gets the answer from the JSON request.
            data = request.get_json()
            answer = data["answer"]

            # Gets the current newest question (Since its only possible to send a request for the newest question).
            questionIndex = len(self.currentManager.questions) - 1
            question = self.currentManager.questions[questionIndex]

            # Checks the answer if its valid, also takes into consideration if the time limit has passed.
            # It returns true or false if the answer is valid.
            result = question.checkAnswer(answer, self.currentManager.timeLimitPassed)

            # Runs when the answer is valid.
            if result:
                # If the time limit has not passed then it will update the difficulty.
                if not self.currentManager.timeLimitPassed:
                    self.currentManager.updateDifficulty(int(answer))
                # This saves the question to the history.
                self.currentManager.saveToHistory()
                # Checks if there is a current timer, it will cancel it if so.
                if self.currentManager.activeTimer is not None:
                    self.currentManager.activeTimer.cancel()
                    print("Returned request, success.")
                # Returns success allowing JavaScript to go to the next question.
                return jsonify({"status": "success", "message": "Answer submitted successfully"})

            # Runs when the answer is invalid stopping js from going to the next question.
            print("Returned request, error.")
            return jsonify({"status": "error", "message": "Answer submitted unsuccessfully"})

## --- NOTES --- ##
#
# Adding the underscore under a function name is a good naming convention for making functions private.
# As it's not required it lets python developers know that this function should only be used by its class.
# This applies to class attributes as well. Python has no real way of making it private.
#
## --- ENDOFNOTES --- ##