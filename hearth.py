from smart_memory import SmartMemory
from demetrius import Demetrius
from automation import Automation
from security import Security, logger
from exceptions import DemetriusOfflineError
import sys

def boot():
    security = Security()

    # Authentication
    if not security.authenticate():
        logger.error("Access denied. Shutting down.")
        sys.exit(1)

    memory   = SmartMemory()
    username = memory.load_user()

    if not username:
        username = input("Hello! What's your name? ")
        memory.save_user(username)

    logger.info(f"Demetrius booting for user: {username}")
    demetrius = Demetrius(username)
    demetrius.security = security
    return demetrius

def run():
    demetrius = boot()
    auto      = Automation()

    print("\nType !help for available commands.\n")

    while True:
        message = input("You: ")

        if message.lower() == "exit":
            logger.info("Demetrius shutdown by user.")
            print(f"[{demetrius.name}]: Goodbye!")
            break
        elif message.lower() == "!clear":
            demetrius.memory.clear_history()
            print("[System]: Memory cleared.")
        elif message.lower() == "!history":
            for row in demetrius.memory.load_history():
                print(row)
        elif message.lower() == "!stats":
            u = len(demetrius.memory.load_user_messages())
            d = len(demetrius.memory.load_jarvis_messages())
            print(f"[System]: You: {u} | Demetrius: {d}")
        elif message.lower() == "!backup":
            result = demetrius.security.backup(encrypt=True)
            print(f"[System]: Backup created: {result}")
        elif message.lower() == "!restore":
            backups = demetrius.security.list_backups()
            if not backups:
                print("[System]: No backups found.")
            else:
                for i, b in enumerate(backups):
                    print(f"  {i} — {b}")
                idx = input("Choose backup number: ")
                if demetrius.security.restore(backups[int(idx)]):
                    print("[System]: Restored successfully.")
                else:
                    print("[System]: Restore failed.")
        elif message.lower() == "!logs":
            import glob
            logs = glob.glob("logs/*.log")
            if logs:
                with open(logs[-1]) as f:
                    print(f.read()[-2000:])
        elif message.lower() == "!sysinfo":
            print(auto.sysinfo())
        elif message.lower().startswith("!open "):
            print(auto.open_app(message[6:].strip()))
        elif message.lower().startswith("!run "):
            print(auto.run_script(message[5:].strip()))
        elif message.lower().startswith("!ls"):
            print(auto.list_files(message[3:].strip() or "."))
        elif message.lower().startswith("!mkdir "):
            print(auto.make_dir(message[7:].strip()))
        elif message.lower().startswith("!find "):
            print(auto.find_file(message[6:].strip()))
        else:
            try:
                response = demetrius.respond(message)
                print(f"[{demetrius.name}]: {response}")
            except DemetriusOfflineError:
                print(f"[{demetrius.name}]: Offline. Start Ollama.")

if __name__ == "__main__":
    run()