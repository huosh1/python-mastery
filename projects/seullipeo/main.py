#!/usr/bin/env python3

import sys
from cli import cli
from shell import shell
from utils.display import print_banner
from utils.logger import setup_logger

# Initialise le logger avec le niveau DEBUG pour développement
logger = setup_logger(level="DEBUG")

def main():
    print_banner()
    logger.info("Seullipeo framework initialisé.")

    if len(sys.argv) > 1:
        logger.debug(f"Arguments détectés : {sys.argv[1:]}")
        cli.run(sys.argv[1:])  # Mode CLI : exploitation directe via options
    else:
        logger.debug("Passage en mode shell interactif.")
        shell.launch()  # Mode REPL interactif (à venir)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Interruption par l'utilisateur (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Erreur inattendue : {e}")
        sys.exit(1)
