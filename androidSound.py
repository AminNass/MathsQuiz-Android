# This is the android media player.
# Current state is that its unstable.
# It can crash if the app is currently lagging.
# It's mainly used for the cheering at the end of each game.
# It should be only used for long mp3 files.
class AndroidMediaPlayer:

    _activePlayers = []
    _MediaPlayer = None

    @classmethod
    def _get(cls):
        if cls._MediaPlayer is None:
            from jnius import autoclass
            cls._MediaPlayer = autoclass("android.media.MediaPlayer")
        return cls._MediaPlayer

    @classmethod
    def playSound(cls, filename):
        import os
        import threading
        from jnius import autoclass

        try:
            soundPath = os.path.abspath(
                os.path.join("static", "sounds", filename)
            )

            if not os.path.isfile(soundPath):
                print(f"File not found: {soundPath}")
                return False

            MediaPlayer = cls._get()
            player = MediaPlayer()

            player.setDataSource(soundPath)

            # ⚡ still synchronous but stable
            player.prepare()
            player.start()

            cls._activePlayers.append(player)

            def cleanup():
                try:
                    player.release()
                except:
                    pass
                try:
                    cls._activePlayers.remove(player)
                except:
                    pass

            duration = player.getDuration()
            threading.Timer(max(duration / 1000 + 1, 2), cleanup).start()

            return True

        except Exception as e:
            print(f"Audio playback failed: {e}")
            return False

import threading
import os
import time
from jnius import autoclass

# This is the android sound pool. Its semi stable and has problems when spammed.
# There are thresholds for the amount of times a sound can be played.
# It uses thread locking to prevent only one thread to access the sound pool at a time.
# It can still crash but mainly because of its incompatibility with pyhon.
class AndroidSoundPool:

    _SoundPool = None
    _soundPool = None
    _sounds = {}

    _lock = threading.Lock()

    _lastPlay = 0.0
    _minInterval = 0.05

    @classmethod
    def _init(cls):
        with cls._lock:
            if cls._SoundPool is not None:
                return

            SoundPoolBuilder = autoclass("android.media.SoundPool$Builder")
            AudioAttributesBuilder = autoclass("android.media.AudioAttributes$Builder")
            AudioAttributes = autoclass("android.media.AudioAttributes")

            attrs = (
                AudioAttributesBuilder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
            )

            cls._soundPool = (
                SoundPoolBuilder()
                .setMaxStreams(4)
                .setAudioAttributes(attrs)
                .build()
            )

            cls._SoundPool = True

    @classmethod
    def preload(cls, key, filename):
        cls._init()

        base_path = os.path.abspath(os.path.join("static", "sounds"))
        filepath = os.path.join(base_path, filename)

        if not os.path.isfile(filepath):
            print(f"Sound not found: {filepath}")
            return False

        # IMPORTANT: load is async → this is still "best effort"
        soundID = cls._soundPool.load(filepath, 1)

        with cls._lock:
            cls._sounds[key] = soundID

        print(f"Preloaded sound: {key} ({soundID})")
        return True

    @classmethod
    def play(cls, key, volume=1.0):
        cls._init()

        now = time.time()

        with cls._lock:

            # rate limit FIRST (prevents spam JNI calls)
            if now - cls._lastPlay < cls._minInterval:
                return False

            soundID = cls._sounds.get(key)

            if soundID is None:
                print(f"Sound not loaded: {key}")
                return False

            cls._lastPlay = now

        try:
            streamID = cls._soundPool.play(
                int(soundID),
                float(volume),
                float(volume),
                1,
                0,
                1.0
            )

            if streamID == 0:
                print("SoundPool rejected playback request")

            return streamID

        except Exception as e:
            print("SoundPool error:", e)
            return False

## --- DEV NOTE --- ##
#
# The android system has a lot of problems.
# Since we are using jnius to interact with java classes there is a very high change of errors happening unexpectedly.
# I tried to debug the problem, but it's really hard to tell what's really going wrong.
# I have tried researching solutions, but It's difficult to find a working solution.
# Simply the problem is incompatibility making playing a sound unstable.
# In a proper android app development environment python would not be used and Java would be used which is a supported language.
# At this state its untable but it works. There are delays when playing audio but there isn't much to do about it.
#
## --- ENDDEVNOTE --- ##