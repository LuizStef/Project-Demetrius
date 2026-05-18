from base import Assistant
from soul import Soul
from smart_memory import SmartMemory
from semantic_memory import SemanticMemory
from core import Core
from permissions import PermissionSystem
from config import NAME, VERSION, VALID_MOODS
from exceptions import InvalidMoodError

def log_action(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

class Demetrius(Assistant):
    def __init__(self, username):
        super().__init__(NAME, VERSION)
        self.__mood = "neutral"
        self.soul = Soul(username, "casual")
        self.memory = SmartMemory()
        self.semantic = SemanticMemory()
        self.core = Core()
        self.permissions = PermissionSystem()

    def get_mood(self):
        return self.__mood

    def set_mood(self, value):
        if value in VALID_MOODS:
            self.__mood = value
        else:
            raise InvalidMoodError(value)

    @log_action
    def respond(self, message):
        # Check permission before doing anything
        if not self.permissions.request_permission(message):
            print(f"[{self.name}]: Action not authorized.")
            return

        self.memory.save_memory("user", message)
        history = list(self.memory.stream_history())
        self.semantic.add(message)
        context = self.semantic.search(message)
        response = self.core.think(message, history, context)
        self.memory.save_memory("jarvis", response)
        print(f"[{self.name}]: {response}")