# Central configuration for Demetrius

NAME = "Demetrius"
VERSION = "2.0"
DB_PATH = "jarvis.db"
VALID_MOODS = ["neutral", "excited", "tired"]
VALID_STYLES = ["formal", "casual", "technical"]

# Available models
OLLAMA_MODELS = ["mistral", "llama3", "gemma", "phi3", "deepseek-r1"]

API_PROVIDERS = {
    "openai":    {"models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"], "url": "https://api.openai.com/v1"},
    "anthropic": {"models": ["claude-haiku-4-5-20251001", "claude-sonnet-4-6"], "url": "https://api.anthropic.com"},
    "groq":      {"models": ["llama3-70b-8192", "mixtral-8x7b-32768"], "url": "https://api.groq.com/openai/v1"},
}

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