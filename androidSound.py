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

class AndroidSoundPool:

    _SoundPool = None
    _soundPool = None
    _sounds = {}

    # ---------------- INIT ----------------
    @classmethod
    def _init(cls):
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
            .setMaxStreams(10)
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
        cls._sounds[key] = soundID

        return True

    @classmethod
    def play(cls, key, volume=1.0):
        cls._init()

        if key not in cls._sounds:
            print(f"Sound not loaded: {key}")
            return False

        soundID = cls._sounds[key]

        cls._soundPool.play(
            soundID,
            volume, volume,
            1,
            0,
            1.0
        )

        return True