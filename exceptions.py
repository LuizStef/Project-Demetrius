class DemetriusOfflineError(Exception):
    def __init__(self):
        super().__init__("Demetrius is offline. Please start Ollama.")

class InvalidMoodError(Exception):
    def __init__(self, mood):
        super().__init__(f"'{mood}' is not a valid mood.")

class UserNotFoundError(Exception):
    def __init__(self, username):
        super().__init__(f"User '{username}' not found.")