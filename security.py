import os
import shutil
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from config import DB_PATH

# ─── LOGGER ───────────────────────────────────────────────────────────────────

def setup_logger():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"demetrius_{datetime.now().strftime('%Y%m')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("demetrius")

logger = setup_logger()

# ─── SECURITY ─────────────────────────────────────────────────────────────────

class Security:
    def __init__(self):
        self.__passkey  = os.environ.get("DEMETRIUS_PASSKEY", None)
        self.__key_file = ".demetrius.key"

    # ── Authentication ─────────────────────────────────────────────────────

    def authenticate(self):
        """Asks for passkey on startup. Returns True if authenticated."""
        if not self.__passkey:
            logger.warning("No passkey set. Skipping authentication.")
            return True

        print("\n" + "─" * 40)
        print("  Demetrius — Authentication")
        print("─" * 40)

        for attempt in range(3):
            entered = input(f"  Passkey ({3 - attempt} attempts left): ")
            if entered == self.__passkey:
                logger.info("Authentication successful.")
                print("─" * 40 + "\n")
                return True
            else:
                logger.warning(f"Failed authentication attempt {attempt + 1}.")
                print("  Incorrect passkey.")

        logger.error("Authentication failed — too many attempts.")
        print("  Access denied.\n")
        return False

    # ── Encryption ─────────────────────────────────────────────────────────

    def _get_or_create_key(self):
        """Loads or creates an encryption key."""
        if os.path.exists(self.__key_file):
            with open(self.__key_file, "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.__key_file, "wb") as f:
            f.write(key)
        logger.info("Encryption key created.")
        return key

    def encrypt_file(self, path):
        """Encrypts a file and saves as .enc."""
        key     = self._get_or_create_key()
        fernet  = Fernet(key)
        enc_path = path + ".enc"

        with open(path, "rb") as f:
            data = f.read()

        with open(enc_path, "wb") as f:
            f.write(fernet.encrypt(data))

        logger.info(f"File encrypted: {enc_path}")
        return enc_path

    def decrypt_file(self, enc_path, output_path):
        """Decrypts a .enc file."""
        key    = self._get_or_create_key()
        fernet = Fernet(key)

        with open(enc_path, "rb") as f:
            data = f.read()

        with open(output_path, "wb") as f:
            f.write(fernet.decrypt(data))

        logger.info(f"File decrypted: {output_path}")
        return output_path

    # ── Backup ─────────────────────────────────────────────────────────────

    def backup(self, encrypt=True):
        """Creates a backup of the database, optionally encrypted."""
        if not os.path.exists(DB_PATH):
            logger.warning("Database not found for backup.")
            return None

        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Backup created: {backup_path}")

        if encrypt:
            enc_path = self.encrypt_file(backup_path)
            os.remove(backup_path)
            logger.info(f"Backup encrypted: {enc_path}")
            return enc_path

        return backup_path

    def restore(self, enc_path):
        """Restores a backup from an encrypted file."""
        try:
            self.decrypt_file(enc_path, DB_PATH)
            logger.info(f"Database restored from: {enc_path}")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    def list_backups(self):
        """Lists all backups."""
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            return []
        return sorted([
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.endswith(".enc") or f.endswith(".db")
        ])