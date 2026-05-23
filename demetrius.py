from base import Assistant
from soul import Soul
from smart_memory import SmartMemory
from semantic_memory import SemanticMemory
from core import Core
from model_manager import ModelManager
from personality import Personality
from voice import Voice
from config import NAME, VERSION, VALID_MOODS
from exceptions import InvalidMoodError

def log_action(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class Demetrius(Assistant):
    def __init__(self, username):
        super().__init__(NAME, VERSION)
        self.__mood      = "neutral"
        self.soul        = Soul(username, "casual")
        self.memory      = SmartMemory()
        self.semantic    = SemanticMemory()
        self.personality = Personality()
        self.models      = ModelManager()
        self.voice       = Voice()

        cfg = self.models.load_config()
        self.core = Core(
            provider=cfg["provider"],
            model=cfg["model"],
            api_key=cfg["api_key"]
        )

    def get_mood(self):
        return self.__mood

    def set_mood(self, value):
        if value in VALID_MOODS:
            self.__mood = value
        else:
            raise InvalidMoodError(value)

    def get_model_info(self):
        return f"{self.core.provider} — {self.core.model}"

    @log_action
    def respond(self, message):
        self.personality.extract_interests(message)
        self.memory.save_memory("user", message)
        history            = list(self.memory.stream_history())
        self.semantic.add(message)
        context            = self.semantic.search(message)
        personality_prompt = self.personality.build_personality_prompt()
        response           = self.core.think(message, history, context, personality_prompt)
        self.memory.save_memory("jarvis", response)

        # Speak the response if voice is enabled
        if self.voice.enabled:
            self.voice.speak(response)

        return response