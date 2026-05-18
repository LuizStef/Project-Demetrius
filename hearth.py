from smart_memory import SmartMemory
from demetrius import Demetrius
from automation import Automation
from exceptions import DemetriusOfflineError

def boot():
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
    demetrius = boot()
    auto = Automation()

    print("\nType !help for available commands.\n")

    while True:
        message = input("You: ")

        # ─── EXIT ───────────────────────────────────
        if message.lower() == "exit":
            print(f"[{demetrius.name}]: Goodbye, {demetrius.soul.get_username()}!")
            break

        # ─── MEMORY ─────────────────────────────────
        elif message.lower() == "!clear":
            demetrius.memory.clear_history()
            print("[System]: Memory cleared.")

        elif message.lower() == "!history":
            for row in demetrius.memory.load_history():
                print(row)

        elif message.lower() == "!stats":
            user_msgs = demetrius.memory.load_user_messages()
            jarvis_msgs = demetrius.memory.load_jarvis_messages()
            print(f"[System]: You sent {len(user_msgs)} messages.")
            print(f"[System]: Demetrius replied {len(jarvis_msgs)} times.")

        # ─── MOOD ───────────────────────────────────
        elif message.lower() == "!mood":
            print(f"[System]: Current mood: {demetrius.get_mood()}")

        elif message.lower().startswith("!mood "):
            mood = message.split(" ")[1]
            try:
                demetrius.set_mood(mood)
                print(f"[System]: Mood changed to {mood}.")
            except Exception as e:
                print(f"[System]: {e}")

        # ─── SYSTEM ─────────────────────────────────
        elif message.lower().startswith("!open "):
            app = message[6:].strip()
            print(auto.open_app(app))

        elif message.lower().startswith("!run "):
            script = message[5:].strip()
            print(auto.run_script(script))

        elif message.lower() == "!sysinfo":
            print(auto.sysinfo())

        # ─── FILES ──────────────────────────────────
        elif message.lower().startswith("!ls"):
            path = message[3:].strip() or "."
            print(auto.list_files(path))

        elif message.lower().startswith("!mkdir "):
            name = message[7:].strip()
            print(auto.make_dir(name))

        elif message.lower().startswith("!find "):
            filename = message[6:].strip()
            print(auto.find_file(filename))

        # ─── BACKUP ─────────────────────────────────
        elif message.lower() == "!backup":
            print(auto.backup())

        # ─── HELP ───────────────────────────────────
        elif message.lower() == "!help":
            print("""
[System]: Available commands:
  exit              → Shutdown Demetrius
  !clear            → Clear conversation history
  !history          → Show conversation history
  !stats            → Show message statistics
  !mood             → Show current mood
  !mood [value]     → Change mood (neutral/excited/tired)
  !sysinfo          → Show system info (CPU, RAM, Disk)
  !open [app]       → Open an application
  !run [script.py]  → Run a Python script
  !ls [path]        → List files in a directory
  !mkdir [name]     → Create a directory
  !find [file]      → Search for a file
  !backup           → Backup the database
""")

        # ─── AI RESPONSE ────────────────────────────
        else:
            try:
                demetrius.respond(message)
            except DemetriusOfflineError:
                print(f"[{demetrius.name}]: I'm offline. Please start Ollama and try again.")

if __name__ == "__main__":
    run()