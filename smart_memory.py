import sqlite3
from datetime import datetime
from config import DB_PATH

class SmartMemory:
    def __init__(self):
        self.__conn = sqlite3.connect(DB_PATH)
        self.__cursor = self.__conn.cursor()
        self.__create_table()

    def __create_table(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        self.__conn.commit()

    def save_memory(self, role, content):
        timestamp = datetime.now().isoformat()
        self.__cursor.execute(
            "INSERT INTO messages (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, timestamp)
        )
        self.__conn.commit()

    def load_history(self):
        self.__cursor.execute("SELECT role, content, timestamp FROM messages ORDER BY id DESC")
        return self.__cursor.fetchall()

    def clear_history(self):
        self.__cursor.execute("DELETE FROM messages")
        self.__conn.commit()

    def search_memory(self, keyword):
        self.__cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE content LIKE ?",
            (f"%{keyword}%",)
        )
        return self.__cursor.fetchall()

    def save_user(self, name):
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS user (name TEXT)")
        self.__cursor.execute("DELETE FROM user")
        self.__cursor.execute("INSERT INTO user (name) VALUES (?)", (name,))
        self.__conn.commit()

    def load_user(self):
        try:
            self.__cursor.execute("SELECT name FROM user")
            result = self.__cursor.fetchone()
            return result[0] if result else None
        except:
            return None

    def load_user_messages(self):
        history = self.load_history()
        return [content for role, content, _ in history if role == "user"]

    def load_jarvis_messages(self):
        history = self.load_history()
        return [content for role, content, _ in history if role == "jarvis"]

    def stream_history(self):
        """Yields one message at a time instead of loading all at once."""
        self.__cursor.execute("SELECT role, content, timestamp FROM messages ORDER BY id ASC")
        for row in self.__cursor.fetchall():
            yield row

    def stream_user_messages(self):
        """Yields only user messages one at a time."""
        for role, content, timestamp in self.stream_history():
            if role == "user":
                yield content