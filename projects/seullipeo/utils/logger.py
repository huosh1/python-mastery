import logging
import os

LOG_FILE = "seullipeo.log"

def setup_logger(name="Seullipeo", level=logging.INFO, to_file=True):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Évite les doublons si logger déjà configuré
    if logger.handlers:
        return logger

    # Format standard : [INFO] 2025-07-28 14:22:31 — message
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s — %(message)s", "%Y-%m-%d %H:%M:%S")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optionnel)
    if to_file:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
