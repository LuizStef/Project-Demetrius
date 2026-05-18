import os
import subprocess
import shutil
import psutil
from datetime import datetime
from permissions import PermissionSystem

class Automation:
    def __init__(self):
        self.permissions = PermissionSystem()

    # ─── SYSTEM ───────────────────────────────────────

    def open_app(self, app):
        """Opens an application."""
        try:
            subprocess.Popen([app])
            return f"Opening {app}..."
        except FileNotFoundError:
            return f"App '{app}' not found."
        except Exception as e:
            return f"Error: {e}"

    def run_script(self, script):
        """Runs a Python script."""
        if not os.path.exists(script):
            return f"Script '{script}' not found."
        try:
            result = subprocess.run(["python", script], capture_output=True, text=True, timeout=30)
            return result.stdout or result.stderr or "Script executed."
        except subprocess.TimeoutExpired:
            return "Script timed out (30s limit)."
        except Exception as e:
            return f"Error: {e}"

    def sysinfo(self):
        """Returns system information."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return (
            f"CPU: {cpu}%\n"
            f"RAM: {ram.percent}% used ({round(ram.used / 1e9, 1)}GB / {round(ram.total / 1e9, 1)}GB)\n"
            f"Disk: {disk.percent}% used ({round(disk.used / 1e9, 1)}GB / {round(disk.total / 1e9, 1)}GB)"
        )

    # ─── FILES ────────────────────────────────────────

    def list_files(self, path="."):
        """Lists files in a directory."""
        if not os.path.exists(path):
            return f"Path '{path}' not found."
        files = os.listdir(path)
        if not files:
            return "Empty directory."
        return "\n".join(files)

    def make_dir(self, name):
        """Creates a directory."""
        try:
            os.makedirs(name, exist_ok=True)
            return f"Directory '{name}' created."
        except Exception as e:
            return f"Error: {e}"

    def find_file(self, filename, search_path="."):
        """Searches for a file recursively."""
        results = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if filename.lower() in file.lower():
                    results.append(os.path.join(root, file))
        if not results:
            return f"File '{filename}' not found."
        return "\n".join(results)

    # ─── DEMETRIUS ────────────────────────────────────

    def backup(self, db_path="jarvis.db"):
        """Creates a backup of the database."""
        if not os.path.exists(db_path):
            return "Database not found."
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.db"
        shutil.copy2(db_path, backup_name)
        return f"Backup created: {backup_name}"