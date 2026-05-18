# Central configuration for Demetrius

NAME = "Demetrius"
VERSION = "2.0"
MODEL = "mistral"
DB_PATH = "jarvis.db"
VALID_MOODS = ["neutral", "excited", "tired"]
VALID_STYLES = ["formal", "casual", "technical"]

# Permission system
CRITICAL_COMMANDS = [
    "rm -rf", "format", "delete all", "wipe",
    "drop database", "shutdown", "mkfs"
]

HIGH_RISK_COMMANDS = [
    "delete", "remove", "uninstall", "kill process",
    "terminate", "sudo", "chmod", "chown"
]

MEDIUM_RISK_COMMANDS = [
    "install", "update", "upgrade", "move file",
    "rename", "overwrite", "modify"
]