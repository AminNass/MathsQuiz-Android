import threading
from flask import Flask, render_template
import webview


class App:
    def __init__(self):
        # Create Flask instance
        self.app = Flask(__name__)

        # Register app menus
        self.appMenus()

        # Start Flask as a background task (Very important, Android has strict memory management)
        self.flaskServer = threading.Thread(target=self.runFlask, daemon=True)
        self.flaskServer.start()

        # 4. Launch the pywebview window container in the main thread
        self.window = webview.create_window('Maths Quiz', 'http://127.0.0.1:5000/', width=390,height=844,resizable=False)
        self.runWindow()

    # Run window
    @staticmethod
    def runWindow(): webview.start()

    # Launch flask server.
    def runFlask(self): self.app.run(host='127.0.0.1', port=5000, debug=False)


    def appMenus(self):
        # Now self.app safely exists and can be targeted by decorators
        @self.app.route('/')
        def index():
            return render_template("index.html")