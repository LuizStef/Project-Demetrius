import ollama
import requests
from datetime import datetime
from config import API_PROVIDERS
from exceptions import DemetriusOfflineError

class Core:
    def __init__(self, provider="ollama", model="mistral", api_key=""):
        self.__provider = provider
        self.__model    = model
        self.__api_key  = api_key
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
            messages.append({
                "role": "system",
                "content": f"Relevant context from memory:\n{chr(10).join(context)}"
            })

        for role, content, _ in history:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        try:
            if self.__provider == "ollama":
                return self._think_ollama(messages)
            else:
                return self._think_api(messages)
        except DemetriusOfflineError:
            raise
        except Exception as e:
            raise DemetriusOfflineError() from e

    def _think_ollama(self, messages):
        try:
            response = ollama.chat(model=self.__model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            raise DemetriusOfflineError() from e

    def _think_api(self, messages):
        provider_config = API_PROVIDERS.get(self.__provider)
        if not provider_config:
            raise DemetriusOfflineError()

        url = f"{provider_config['url']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.__api_key}",
            "Content-Type": "application/json",
        }

        if self.__provider == "anthropic":
            headers = {
                "x-api-key": self.__api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
            url = "https://api.anthropic.com/v1/messages"
            system = next((m["content"] for m in messages if m["role"] == "system"), "")
            msgs = [m for m in messages if m["role"] != "system"]
            payload = {"model": self.__model, "max_tokens": 1024, "system": system, "messages": msgs}
        else:
            payload = {"model": self.__model, "messages": messages}

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if self.__provider == "anthropic":
            return data["content"][0]["text"]
        return data["choices"][0]["message"]["content"]

    @property
    def provider(self):
        return self.__provider

    @property
    def model(self):
        return self.__model