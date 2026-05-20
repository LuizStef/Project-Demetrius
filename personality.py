import sqlite3
import json
from datetime import datetime
from config import DB_PATH

class Personality:
    def __init__(self):
        self.__conn   = sqlite3.connect(DB_PATH)
        self.__cursor = self.__conn.cursor()
        self.__create_tables()

    def __create_tables(self):
        self.__cursor.executescript("""
            CREATE TABLE IF NOT EXISTS personality (
                id      INTEGER PRIMARY KEY,
                profile TEXT
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                message   TEXT,
                response  TEXT,
                rating    INTEGER,
                timestamp TEXT
            );
        """)
        self.__conn.commit()
        if not self.__load_raw():
            self.__save_raw(self.__default_profile())

    def __default_profile(self):
        return {
            "style":      "casual",
            "interests":  [],
            "vocabulary": [],
            "feedback_positive": [],
            "feedback_negative": [],
            "updated_at": datetime.now().isoformat()
        }

    def __load_raw(self):
        self.__cursor.execute("SELECT profile FROM personality WHERE id = 1")
        result = self.__cursor.fetchone()
        return json.loads(result[0]) if result else None

    def __save_raw(self, profile):
        profile["updated_at"] = datetime.now().isoformat()
        self.__cursor.execute("DELETE FROM personality")
        self.__cursor.execute(
            "INSERT INTO personality (id, profile) VALUES (1, ?)",
            (json.dumps(profile),)
        )
        self.__conn.commit()

    def get_profile(self):
        return self.__load_raw() or self.__default_profile()

    def update_interests(self, topics: list):
        """Adds new topics to interests list."""
        profile = self.get_profile()
        for t in topics:
            if t not in profile["interests"]:
                profile["interests"].append(t)
        profile["interests"] = profile["interests"][-30:]  # keep last 30
        self.__save_raw(profile)

    def update_vocabulary(self, words: list):
        """Tracks words the user uses frequently."""
        profile = self.get_profile()
        for w in words:
            if w not in profile["vocabulary"]:
                profile["vocabulary"].append(w)
        profile["vocabulary"] = profile["vocabulary"][-50:]  # keep last 50
        self.__save_raw(profile)

    def add_feedback(self, message, response, rating):
        """Saves feedback. rating: 1 = good, -1 = bad."""
        profile = self.get_profile()
        timestamp = datetime.now().isoformat()

        self.__cursor.execute(
            "INSERT INTO feedback (message, response, rating, timestamp) VALUES (?, ?, ?, ?)",
            (message, response, rating, timestamp)
        )
        self.__conn.commit()

        if rating == 1:
            profile["feedback_positive"].append(response[:80])
            profile["feedback_positive"] = profile["feedback_positive"][-10:]
        else:
            profile["feedback_negative"].append(response[:80])
            profile["feedback_negative"] = profile["feedback_negative"][-10:]

        self.__save_raw(profile)

    def build_personality_prompt(self):
        """Builds a prompt snippet describing the user's personality profile."""
        profile = self.get_profile()
        parts   = []

        if profile["interests"]:
            parts.append(f"User interests: {', '.join(profile['interests'][-10:])}.")

        if profile["vocabulary"]:
            parts.append(f"User often uses these words/expressions: {', '.join(profile['vocabulary'][-10:])}.")

        if profile["feedback_positive"]:
            parts.append("The user liked responses that were: " +
                         " | ".join(profile["feedback_positive"][-3:]))

        if profile["feedback_negative"]:
            parts.append("The user disliked responses that were: " +
                         " | ".join(profile["feedback_negative"][-3:]))

        return "\n".join(parts) if parts else ""

    def extract_interests(self, text):
        """Simple keyword extractor for interests."""
        keywords = [
            "python", "programming", "music", "guitar", "biology", "science",
            "ai", "machine learning", "linux", "arch", "raspberry", "automation",
            "code", "database", "security", "voice", "design", "ui", "math"
        ]
        found = [k for k in keywords if k in text.lower()]
        if found:
            self.update_interests(found)