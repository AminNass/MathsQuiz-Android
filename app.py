import threading
from flask import Flask, render_template, request, jsonify
import webview
import mathsQuiz


# NATIVE ANDROID MULTIMEDIA ENGINE
MediaPlayer = None
Context = None
try:
    # Attempt to load the native Android Java hooks directly
    from jnius import autoclass
    MediaPlayer = autoclass('android.media.MediaPlayer')
    Context = autoclass('org.kivy.android.PythonActivity').mActivity
    print("Android Native Audio Engine initialized successfully.")
except Exception as e:
    # If this fails, we are definitely testing locally on a PC
    MediaPlayer = None
    Context = None
    print(f"Jnius or Android classes not found. Defaulting to PC Mode. (Error: {e})")

import os
from jnius import autoclass

# CRITICAL: Keeps a strong reference alive in memory so Python's Garbage
# Collector does not destroy the player object while Android is preparing it.
_active_audio_handles = []


def playNativeSound(filename):
    """Plays UI audio assets flawlessly using explicit IPC-safe ParcelFileDescriptors."""
    if MediaPlayer is None or Context is None:
        print(f"[PC Emulator Mode] Playing sound: {filename}")
        return

    try:
        # 1. Target the local internal file path
        abs_path = os.path.abspath(f"static/sounds/{filename}")
        if not os.path.exists(abs_path):
            print(f"Native audio error: Target file missing at {abs_path}")
            return

        # 2. Import core Android OS components
        ParcelFileDescriptor = autoclass('android.os.ParcelFileDescriptor')
        JavaFile = autoclass('java.io.File')
        MediaPlayerClass = autoclass('android.media.MediaPlayer')

        # 3. Wrap file in an IPC-safe Parcel descriptor
        j_file = JavaFile(abs_path)
        pfd = ParcelFileDescriptor.open(j_file, ParcelFileDescriptor.MODE_READ_ONLY)

        # 4. Measure size metrics
        file_length = os.path.getsize(abs_path)

        # 5. Initialize the media player engine instance
        mp = MediaPlayerClass()

        # 6. Pass the duplicated native descriptor handle with accurate bounds
        mp.setDataSource(pfd.getFileDescriptor(), 0, file_length)

        # 7. Warm up audio hardware streams synchronously
        mp.prepare()

        # Protect the active components from Python's memory cleanup cycles
        _active_audio_handles.append((mp, pfd))

        # 8. Fire the sound effect
        mp.start()

        # 9. Clean up all system resource handles when the sound finishes playing
        def on_playback_complete(player_instance):
            try:
                player_instance.release()
                pfd.close()

                # Locate and clear this handle from active memory tracking
                for item in _active_audio_handles:
                    if item[0] == player_instance:
                        _active_audio_handles.remove(item)
                        break
                print(f"Successfully released native audio resources for {filename}")
            except Exception as cleanup_error:
                print(f"Audio cleanup warning: {cleanup_error}")

        mp.setOnCompletionListener(on_playback_complete)

    except Exception as e:
        print(f"Native audio engine playback error: {e}")


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
        def trigger_sound_effect(filename):
            playNativeSound(filename)
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



