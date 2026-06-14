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


class AndroidSoundPool:

    _SoundPool = None
    _soundPool = None
    _sounds = {}

    _lock = threading.Lock()

    _lastPlay = 0.0
    _minInterval = 0.05

    # -------------------------
    # INIT SOUND POOL
    # -------------------------
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

    # -------------------------
    # PRELOAD SOUND
    # -------------------------
    @classmethod
    def preload(cls, key, filename):
        cls._init()

        base_path = os.path.abspath(os.path.join("static", "sounds"))
        filepath = os.path.join(base_path, filename)

        if not os.path.isfile(filepath):
            print(f"Sound not found: {filepath}")
            return False

        soundID = cls._soundPool.load(filepath, 1)

        with cls._lock:
            cls._sounds[key] = soundID

        print(f"Preloaded sound: {key} ({soundID})")
        return True

    # -------------------------
    # PLAY SOUND (THREAD SAFE)
    # -------------------------
    @classmethod
    def play(cls, key, volume=1.0):
        cls._init()

        now = time.time()

        with cls._lock:
            # rate limit
            if now - cls._lastPlay < cls._minInterval:
                return False

            soundID = cls._sounds.get(key)
            if soundID is None:
                print(f"Sound not loaded: {key}")
                return False

            cls._lastPlay = now

        try:
            streamID = cls._soundPool.play(
                soundID,
                volume,
                volume,
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