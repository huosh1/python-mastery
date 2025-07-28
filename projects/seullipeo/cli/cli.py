# cli/cli.py

import argparse
import logging
from exploits import suid, cron  # tu ajouteras d'autres modules ici au fur et à mesure

logger = logging.getLogger("Seullipeo")

def run(args):
    parser = argparse.ArgumentParser(
        prog="Seullipeo",
    )

    #Arguments CLI disponibles
    parser.add_argument("--scan", action="store_true", help="Effectue un scan global des vecteurs d'escalade")
    parser.add_argument("--suid", action="store_true", help="Lance le module d'exploitation SUID")
    parser.add_argument("--cron", action="store_true", help="Lance le module d'exploitation CRON")
    parser.add_argument("--debug", action="store_true", help="Affiche les logs de débogage")
    parser.add_argument("--version", action="store_true", help="Affiche la version de Seullipeo")
    parser.add_argument("--exec", action="store_true", help="Exécute automatiquement les binaires détectés via GTFOBins")

    
    options = parser.parse_args(args)

    #Gestion des options
    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("[DEBUG] Mode débogage activé.")

    if options.version:
        print("Seullipeo v0.1 – Early Sleeper Phase")
        return

    if options.scan:
        logger.info("[*] Scan global (à implémenter prochainement)")
        # ➜ ici tu pourras appeler tous les modules en détection passive

    if options.suid:
        logger.info("[*] Lancement du module SUID")
        suid.run(execute=options.exec)

    if options.cron:
        logger.info("[*] Lancement du module CRON")
        cron.run(execute=options.exec)

    

    # Si aucun argument actif
    if not any(vars(options).values()):
        parser.print_help()
