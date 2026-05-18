from smart_memory import SmartMemory
from demetrius import Demetrius
from exceptions import DemetriusOfflineError

def boot():
    """Initializes and boots Demetrius."""
    memory = SmartMemory()
    username = memory.load_user()

    if not username:
        username = input("Hello! What's your name? ")
        memory.save_user(username)

    demetrius = Demetrius(username)
    demetrius.soul.greet()
    demetrius.introduce()

    return demetrius

def run():
    """Main loop."""
    demetrius = boot()

    while True:
        message = input("You: ")

        if message.lower() == "exit":
            print(f"[{demetrius.name}]: Goodbye, {demetrius.soul.get_username()}!")
            break
        elif message.lower() == "!clear":
            demetrius.memory.clear_history()
            print("[System]: Memory cleared.")
        elif message.lower() == "!history":
            for row in demetrius.memory.load_history():
                print(row)
        elif message.lower() == "!mood":
            print(f"[System]: Current mood: {demetrius.get_mood()}")
        elif message.lower() == "!stats":
            user_msgs = demetrius.memory.load_user_messages()
            jarvis_msgs = demetrius.memory.load_jarvis_messages()
            print(f"[System]: You sent {len(user_msgs)} messages.")
            print(f"[System]: Demetrius replied {len(jarvis_msgs)} times.")
        elif message.lower().startswith("!mood "):
            mood = message.split(" ")[1]
            try:
                demetrius.set_mood(mood)
                print(f"[System]: Mood changed to {mood}.")
            except Exception as e:
                print(f"[System]: {e}")
        else:
            try:
                demetrius.respond(message)
            except DemetriusOfflineError:
                print(f"[{demetrius.name}]: I'm offline. Please start Ollama and try again.")

if __name__ == "__main__":
    run()