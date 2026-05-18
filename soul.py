from config import VALID_STYLES

class Soul:
    def __init__(self, name, style="casual"):
        self.__username = name
        self.__style = style

    def get_username(self):
        return self.__username

    def set_username(self, value):
        self.__username = value

    def get_style(self):
        return self.__style

    def set_style(self, value):
        if value in VALID_STYLES:
            self.__style = value
        else:
            print(f"Invalid style. Choose from: {VALID_STYLES}")

    def greet(self):
        if self.__style == "formal":
            print(f"Hello, {self.__username}. How can I help you?")
        elif self.__style == "casual":
            print(f"Hey, {self.__username}! How can I assist you?")
        elif self.__style == "technical":
            print(f"Hello, {self.__username}. Waiting for command.")