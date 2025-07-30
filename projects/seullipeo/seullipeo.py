#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seullipeo (슬리퍼) - Framework d'escalade de privilèges Linux
Point d'entrée principal
"""

import sys
import os
import argparse
from pathlib import Path

# Ajout du répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent))

from utils.display import show_banner, print_colored
from utils.logger import setup_logger
from cli.cli import main as cli_main
from shell.shell import InteractiveShell

__version__ = "1.0.0"
__author__ = "huoshi"

def show_version():
    """Affiche les informations de version"""
    print_colored(f"Seullipeo v{__version__}", "cyan")
    print_colored(f"Framework d'escalade de privilèges Linux", "white")
    print_colored(f"Auteur: {__author__}", "yellow")

def check_requirements():
    """Vérifie les prérequis système"""
    if os.geteuid() != 0:
        print_colored("[!] Attention: Vous n'êtes pas root. Certains modules pourraient ne pas fonctionner.", "yellow")
    
    if sys.version_info < (3, 6):
        print_colored("[-] Python 3.6+ requis", "red")
        sys.exit(1)

def setup_directories():
    """Crée les répertoires nécessaires"""
    directories = ['output', 'logs', 'sessions']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Fonction principale"""
    # Configuration initiale
    setup_directories()
    setup_logger()
    check_requirements()
    
    # Parser principal
    parser = argparse.ArgumentParser(
        description="Seullipeo (슬리퍼) - Framework d'escalade de privilèges Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  Mode CLI:
    python3 main.py --scan --cron --suid
    python3 main.py --exploit --passwd --output results.txt
    python3 main.py --aggressive --json results.json
    
  Mode Shell interactif:
    python3 main.py --shell
        """
    )
    
    # Options principales
    parser.add_argument('--shell', action='store_true', 
                       help='Lance le shell interactif')
    parser.add_argument('--version', action='store_true',
                       help='Affiche la version')
    parser.add_argument('--banner', action='store_true',
                       help='Affiche uniquement la bannière')
    
    # Si aucun argument n'est fourni, afficher l'aide
    if len(sys.argv) == 1:
        show_banner()
        print_colored("\n[*] Utilisez --help pour voir les options disponibles", "blue")
        print_colored("[*] Utilisez --shell pour le mode interactif", "blue")
        parser.print_help()
        sys.exit(0)
    
    args, remaining_args = parser.parse_known_args()
    
    # Gestion des options principales
    if args.version:
        show_version()
        sys.exit(0)
    
    if args.banner:
        show_banner()
        sys.exit(0)
    
    if args.shell:
        # Mode shell interactif
        show_banner()
        shell = InteractiveShell()
        shell.run()
    else:
        # Mode CLI avec arguments
        # Repasser tous les arguments au CLI
        sys.argv = [sys.argv[0]] + remaining_args
        cli_main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n[!] Interruption par l'utilisateur", "yellow")
        sys.exit(0)
    except Exception as e:
        print_colored(f"[-] Erreur critique: {str(e)}", "red")
        sys.exit(1)