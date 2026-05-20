import os
import sqlite3
from config import DB_PATH, OLLAMA_MODELS, API_PROVIDERS

class ModelManager:
    def __init__(self):
        self.__conn = sqlite3.connect(DB_PATH)
        self.__cursor = self.__conn.cursor()
        self.__create_table()

    def __create_table(self):
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_config (
                id INTEGER PRIMARY KEY,
                provider TEXT,
                model TEXT,
                api_key TEXT
            )
        """)
        self.__conn.commit()

    def save_config(self, provider, model, api_key=""):
        self.__cursor.execute("DELETE FROM model_config")
        self.__cursor.execute(
            "INSERT INTO model_config (provider, model, api_key) VALUES (?, ?, ?)",
            (provider, model, api_key)
        )
        self.__conn.commit()

    def load_config(self):
        try:
            self.__cursor.execute("SELECT provider, model, api_key FROM model_config")
            result = self.__cursor.fetchone()
            if result:
                return {"provider": result[0], "model": result[1], "api_key": result[2]}
        except:
            pass
        return {"provider": "ollama", "model": "mistral", "api_key": ""}

    def list_ollama_models(self):
        """Returns locally available Ollama models."""
        try:
            import ollama
            models = ollama.list()
            return [m["model"].split(":")[0] for m in models.get("models", [])]
        except:
            return OLLAMA_MODELS

    def list_api_models(self, provider):
        return API_PROVIDERS.get(provider, {}).get("models", [])