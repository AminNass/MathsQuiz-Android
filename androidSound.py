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

class AndroidSoundPool:

    _SoundPool = None
    _soundPool = None
    _sounds = {}

    _lock = threading.Lock()

    # Anti-spam protection
    _lastPlay = 0.0
    _minInterval = 0.05  # 50ms = max 20 plays/sec

    @classmethod
    def _init(cls):
        with cls._lock:
            if cls._SoundPool is not None:
                return

            from jnius import autoclass

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
                .setMaxStreams(2)
                .setAudioAttributes(attrs)
                .build()
            )

            cls._SoundPool = True

    @classmethod
    def preload(cls, key, filename):
        import os

        cls._init()

        filepath = os.path.join("static", "sounds", filename)

        if not os.path.isfile(filepath):
            print(f"Sound not found: {filepath}")
            return False

        soundID = cls._soundPool.load(filepath, 1)

        with cls._lock:   # ✅ protect shared dict write
            cls._sounds[key] = soundID

        print(f"Preloaded sound: {key} ({soundID})")
        return True

    @classmethod
    def play(cls, key, volume=1.0):
        import time

        cls._init()

        now = time.time()

        with cls._lock:
            # atomic rate-limit check + update
            if now - cls._lastPlay < cls._minInterval:
                return False
            cls._lastPlay = now

            if key not in cls._sounds:
                print(f"Sound not loaded: {key}")
                return False

            soundID = cls._sounds[key]

        # IMPORTANT: play() is OUTSIDE lock (prevents blocking audio thread)
        print(f"Playing sound: {key} ({soundID})")

        streamID = cls._soundPool.play(
            soundID,
            volume,
            volume,
            1,
            0,
            1.0
        )

        print(f"Stream ID: {streamID}")

        if streamID == 0:
            print("SoundPool rejected playback request")

        return streamID