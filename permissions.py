import os
from config import CRITICAL_COMMANDS, HIGH_RISK_COMMANDS, MEDIUM_RISK_COMMANDS

class PermissionSystem:
    def __init__(self):
        self.__passkey = os.environ.get("DEMETRIUS_PASSKEY", None)

    def get_risk_level(self, command):
        """Returns the risk level of a command."""
        command_lower = command.lower()

        for trigger in CRITICAL_COMMANDS:
            if trigger in command_lower:
                return "critical"

        for trigger in HIGH_RISK_COMMANDS:
            if trigger in command_lower:
                return "high"

        for trigger in MEDIUM_RISK_COMMANDS:
            if trigger in command_lower:
                return "medium"

        return "low"

    def request_permission(self, command):
        """
        Returns True if the command is allowed, False otherwise.
        low      → always allowed
        medium   → asks y/n
        high     → asks passkey
        critical → blocked
        """
        level = self.get_risk_level(command)

        if level == "low":
            return True

        elif level == "medium":
            confirm = input(f"[Demetrius]: This action requires confirmation. Proceed? (y/n): ")
            return confirm.lower() == "y"

        elif level == "high":
            if not self.__passkey:
                print("[Security]: No passkey set. Run: export DEMETRIUS_PASSKEY='yourpasskey'")
                return False
            entered = input("[Security]: Enter your passkey: ")
            return entered == self.__passkey

        elif level == "critical":
            print("[Security]: This command is blocked. It's on the critical blacklist.")
            return False
    