import os
import threading
from flask import Flask, render_template, request, jsonify
import webview
import mathsQuiz

# Global list to protect active players from Python garbage collection mid-playback
_active_audio_players = []


def play_native_sound(filename):
    """
    Plays audio effects using native Android MediaPlayer via raw File Descriptors.
    Bypasses Android storage sandboxing completely and drops back to console logging on PC.
    """
    sound_path = os.path.abspath(f"static/sounds/{filename}")
    if not os.path.exists(sound_path):
        print(f"--- Audio Error: File missing at {sound_path} ---")
        return

    try:
        from jnius import autoclass

        MediaPlayer = autoclass('android.media.MediaPlayer')
        FileInputStream = autoclass('java.io.FileInputStream')

        mp = MediaPlayer()
        fis = FileInputStream(sound_path)
        fd = fis.getFD()

        # Passing raw file descriptors avoids Android OS path security policy restrictions
        mp.setDataSource(fd, 0, os.path.getsize(sound_path))
        mp.prepare()

        # Keep track of instance so Python memory management doesn't delete it while playing
        _active_audio_players.append(mp)
        mp.start()

        # Clean up system handles when sound effect concludes
        def on_complete(player_instance):
            try:
                player_instance.release()
                if player_instance in _active_audio_players:
                    _active_audio_players.remove(player_instance)
            except Exception as ce:
                print(f"Audio memory release exception: {ce}")

        mp.setOnCompletionListener(on_complete)
        fis.close()

    except ImportError:
        # Graceful fallback so your code still executes smoothly during PC desktop testing
        print(f"[PC Environment Mode] Audio Triggered: {filename}")
    except Exception as e:
        print(f"Native audio sub-system crash: {e}")

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

        @self.app.route('/api/play/<filename>')
        def playSound(filename):
            # Directly hand off back-end audio requests straight to the native hardware player
            play_native_sound(filename)
            return jsonify({"status": "played"})

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
                    print("Returned request, success.")
                return jsonify({"status": "success", "message": "Answer submitted successfully"})

            print("Returned request, error.")
            return jsonify({"status": "error", "message": "Answer submitted unsuccessfully"})



