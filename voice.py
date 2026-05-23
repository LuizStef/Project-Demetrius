import threading
import tempfile
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
import whisper
import pyttsx3
from config import DB_PATH

class Voice:
    def __init__(self):
        self.__model    = whisper.load_model("base")
        self.__engine   = pyttsx3.init()
        self.__rate     = 175
        self.__volume   = 1.0
        self.__speaking = False
        self.__enabled  = True
        self._configure_engine()

    def _configure_engine(self):
        self.__engine.setProperty("rate",   self.__rate)
        self.__engine.setProperty("volume", self.__volume)
        voices = self.__engine.getProperty("voices")
        if voices:
            self.__engine.setProperty("voice", voices[0].id)

    def speak(self, text):
        """Speaks text in a background thread."""
        if not self.__enabled:
            return
        def _speak():
            self.__speaking = True
            self.__engine.say(text)
            self.__engine.runAndWait()
            self.__speaking = False
        threading.Thread(target=_speak, daemon=True).start()

    def listen(self, duration=5, sample_rate=16000):
        """Records audio and returns transcribed text."""
        try:
            print("[Voice]: Recording...")
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )
            sd.wait()
            print("[Voice]: Processing...")

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                sf.write(temp_path, audio, sample_rate)

            result = self.__model.transcribe(temp_path, language=None)
            os.unlink(temp_path)

            text = result["text"].strip()
            print(f"[Voice]: Heard: '{text}'")
            return text

        except Exception as e:
            print(f"[Voice]: Error: {e}")
            return ""

    def toggle(self):
        self.__enabled = not self.__enabled
        return self.__enabled

    @property
    def enabled(self):
        return self.__enabled

    @property
    def speaking(self):
        return self.__speaking