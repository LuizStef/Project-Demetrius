import ollama
from datetime import datetime
from config import MODEL
from exceptions import DemetriusOfflineError

class Core:
    def __init__(self):
        self.__model = MODEL
        today = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.__system_prompt = f"""You are Demetrius, a personal AI assistant created by Luiz Stefanelli.
You are helpful, intelligent and slightly informal.
Today is {today}.
Always respond concisely and directly.
Always respond in the same language the user is speaking.
Keep your language clean and respectful."""

    def think(self, message, history=[], context=[]):
        messages = [{"role": "system", "content": self.__system_prompt}]

        if context:
            context_text = "\n".join(context)
            messages.append({
                "role": "system",
                "content": f"Relevant context from memory:\n{context_text}"
            })

        for role, content, _ in history:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        try:
            response = ollama.chat(model=self.__model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            raise DemetriusOfflineError() from e