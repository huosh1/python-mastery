#!/usr/bin/env python3
"""
Gieokja (기억자) - The Rememberer
Un compagnon de mémoire qui capture vos sessions CTF via un shell modifié
"""

import sys
import os
import signal
import argparse
import subprocess
import threading
import time
import re
import json
from datetime import datetime
from pathlib import Path
import readline
import atexit

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tracker import CommandTracker
from core.writer import WriteupWriter
from core.hooks import HookManager
from utils.logger import setup_logger
from utils.colors import Colors


class GieokjaWrapper:
    """Wrapper qui intercepte les commandes via PROMPT_COMMAND"""
    
    def __init__(self, session_name=None):
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self.logger = setup_logger()
        
        # Composants
        self.tracker = CommandTracker(self.session_name)
        self.writer = WriteupWriter(self.session_name)
        self.hook_manager = HookManager()
        
        # État
        self.running = True
        self.command_file = f"/tmp/gieokja_{os.getpid()}.cmd"
        self.output_file = f"/tmp/gieokja_{os.getpid()}.out"
        
        # Thread de monitoring
        self.monitor_thread = None
        
        # Créer les répertoires
        self._create_directories()
        
    def _create_directories(self):
        """Créer la structure de répertoires"""
        for dir_name in ["data", "logs", "templates"]:
            Path(dir_name).mkdir(exist_ok=True)
    
    def start(self):
        """Démarrer Gieokja avec une approche différente"""
        # Message de bienvenue
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}║  🧠 Gieokja - The Rememberer                               ║{Colors.RESET}")
        print(f"{Colors.CYAN}║  Session: {self.session_name:<34}║{Colors.RESET}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Capture activée via shell modifié{Colors.RESET}")
        print(f"\nCommandes Gieokja (taper directement dans le terminal):")
        print(f"  {Colors.YELLOW}gieokja-note <texte>{Colors.RESET} - Ajouter une note")
        print(f"  {Colors.YELLOW}gieokja-flag [texte]{Colors.RESET} - Marquer un flag")
        print(f"  {Colors.YELLOW}gieokja-todo <texte>{Colors.RESET} - Ajouter un TODO")
        print(f"  {Colors.YELLOW}gieokja-save{Colors.RESET} - Forcer la sauvegarde")
        print(f"  {Colors.YELLOW}gieokja-status{Colors.RESET} - Voir le statut")
        print(f"  {Colors.YELLOW}gieokja-stop{Colors.RESET} - Arrêter Gieokja\n")
        
        # Démarrer le tracking
        self.tracker.start()
        
        # Créer les fonctions shell
        self._setup_shell_integration()
        
        # Démarrer le thread de monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_commands)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Démarrer un nouveau shell avec les fonctions
        self._start_instrumented_shell()
    
    def _setup_shell_integration(self):
        """Créer le script d'intégration shell"""
        integration_script = f"""
# Gieokja Shell Integration
export GIEOKJA_SESSION="{self.session_name}"
export GIEOKJA_CMD_FILE="{self.command_file}"
export GIEOKJA_OUT_FILE="{self.output_file}"

# Fonction pour capturer les commandes
gieokja_capture() {{
    local exit_code=$?
    history 1 | sed 's/^[ ]*[0-9]*[ ]*//' > "$GIEOKJA_CMD_FILE"
    echo "$exit_code" >> "$GIEOKJA_CMD_FILE"
    return $exit_code
}}

# Commandes Gieokja
gieokja-note() {{
    echo "GIEOKJA:NOTE:$*" >> "$GIEOKJA_CMD_FILE"
    echo -e "\\033[32m✓ Note ajoutée\\033[0m"
}}

gieokja-flag() {{
    if [ $# -eq 0 ]; then
        echo "GIEOKJA:FLAG:AUTO" >> "$GIEOKJA_CMD_FILE"
    else
        echo "GIEOKJA:FLAG:$*" >> "$GIEOKJA_CMD_FILE"
    fi
    echo -e "\\033[32m✓ Flag marqué\\033[0m"
}}

gieokja-todo() {{
    echo "GIEOKJA:TODO:$*" >> "$GIEOKJA_CMD_FILE"
    echo -e "\\033[32m✓ TODO ajouté\\033[0m"
}}

gieokja-save() {{
    echo "GIEOKJA:SAVE:" >> "$GIEOKJA_CMD_FILE"
    echo -e "\\033[32m✓ Write-up sauvegardé\\033[0m"
}}

gieokja-status() {{
    echo "GIEOKJA:STATUS:" >> "$GIEOKJA_CMD_FILE"
    sleep 0.1  # Donner le temps au monitor de traiter
}}

gieokja-stop() {{
    echo "GIEOKJA:STOP:" >> "$GIEOKJA_CMD_FILE"
    echo -e "\\033[33m⏹ Arrêt de Gieokja...\\033[0m"
    sleep 0.5
    exit
}}

# Configurer PROMPT_COMMAND pour capturer après chaque commande
export PROMPT_COMMAND="gieokja_capture; ${{PROMPT_COMMAND}}"

# Message de démarrage
echo -e "\\033[36m🧠 Shell Gieokja actif - Toutes les commandes sont capturées\\033[0m"
"""
        
        # Écrire le script d'intégration
        self.integration_file = f"/tmp/gieokja_integration_{os.getpid()}.sh"
        with open(self.integration_file, 'w') as f:
            f.write(integration_script)
    
    def _start_instrumented_shell(self):
        """Démarrer un shell avec l'intégration Gieokja"""
        shell = os.environ.get('SHELL', '/bin/bash')
        
        # Lancer le shell avec le script d'intégration
        subprocess.run([shell, "--rcfile", self.integration_file])
        
        # Nettoyer quand on sort
        self.stop()
    
    def _monitor_commands(self):
        """Monitorer les fichiers de commandes"""
        last_command = None
        
        while self.running:
            try:
                if os.path.exists(self.command_file):
                    with open(self.command_file, 'r') as f:
                        lines = f.readlines()
                    
                    if lines:
                        # Nettoyer le fichier
                        os.truncate(self.command_file, 0)
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Traiter les commandes spéciales
                            if line.startswith("GIEOKJA:"):
                                self._handle_gieokja_command(line)
                            else:
                                # C'est une commande normale
                                if line != last_command and not line.isdigit():
                                    # Capturer la sortie si possible
                                    output = self._try_capture_output(line)
                                    self.tracker.track_command(line, output or "")
                                    last_command = line
                                    
                                    # Traiter avec les hooks
                                    context = {'command': line, 'output': output or ""}
                                    self.hook_manager.process(context)
                
                time.sleep(0.1)
                
            except Exception as e:
                # Ne logger que les erreurs importantes, pas les erreurs de regex
                if "expected string" not in str(e):
                    self.logger.error(f"Erreur dans monitor: {e}")
                time.sleep(0.5)
    
    def _handle_gieokja_command(self, line):
        """Traiter les commandes Gieokja spéciales"""
        parts = line.split(':', 2)
        if len(parts) < 2:
            return
        
        cmd_type = parts[1]
        data = parts[2] if len(parts) > 2 else ""
        
        if cmd_type == "NOTE":
            self.tracker.add_note(data)
            
        elif cmd_type == "FLAG":
            if data == "AUTO":
                self.tracker.mark_as_flag()
            else:
                self.tracker.mark_as_flag(data)
        
        elif cmd_type == "TODO":
            self.tracker.add_todo(data)
        
        elif cmd_type == "SAVE":
            self._save_writeup()
        
        elif cmd_type == "STATUS":
            self._show_status()
        
        elif cmd_type == "STOP":
            self.running = False
    
    def _try_capture_output(self, command):
        """Essayer de capturer la sortie d'une commande (best effort)"""
        # Pour l'instant, on retourne None
        # Dans une version future, on pourrait implémenter une capture plus sophistiquée
        return None
    
    def _show_status(self):
        """Afficher le statut"""
        data = self.tracker.get_session_data()
        
        print(f"\n{Colors.CYAN}╔══════════════════════════════════════╗")
        print(f"║         Statut Gieokja               ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║ Session: {data['session_name']:<28}║")
        print(f"║ Commandes: {len(data['commands']):<26}║")
        print(f"║ Flags: {len(data['flags']):<30}║")
        print(f"║ Notes: {len(data['notes']):<30}║")
        print(f"║ TODOs: {len(data['todos']):<30}║")
        print(f"╚══════════════════════════════════════╝{Colors.RESET}")
        
        if data['flags']:
            print(f"\n{Colors.GREEN}Derniers flags:{Colors.RESET}")
            for flag in data['flags'][-3:]:
                print(f"  • {flag['flag']}")
        print()
    
    def _save_writeup(self):
        """Sauvegarder le write-up"""
        session_data = self.tracker.get_session_data()
        self.writer.write_session_data(session_data)
    
    def stop(self):
        """Arrêter Gieokja"""
        self.running = False
        
        # Sauvegarder une dernière fois
        self._save_writeup()
        
        # Nettoyer les fichiers temporaires
        for f in [self.command_file, self.output_file, self.integration_file]:
            if os.path.exists(f):
                os.remove(f)
        
        print(f"\n{Colors.GREEN}✓ Session Gieokja terminée")
        print(f"📄 Write-up sauvegardé: {self.writer.output_path}{Colors.RESET}")


def setup_bash_alias():
    """Configurer un alias bash pour lancer Gieokja facilement"""
    alias_command = f"""
# Alias Gieokja
alias gieokja='python3 {os.path.abspath(__file__)}'
alias gieokja-start='python3 {os.path.abspath(__file__)}'
"""
    
    bashrc = os.path.expanduser("~/.bashrc")
    
    # Vérifier si déjà installé
    with open(bashrc, 'r') as f:
        if 'alias gieokja=' in f.read():
            print("Les alias Gieokja sont déjà installés")
            return
    
    # Ajouter les alias
    with open(bashrc, 'a') as f:
        f.write(alias_command)
    
    print(f"{Colors.GREEN}✓ Alias installés dans ~/.bashrc")
    print(f"Rechargez votre shell: source ~/.bashrc")
    print(f"Puis lancez avec: gieokja ou gieokja-start{Colors.RESET}")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Gieokja - Capture automatique de sessions CTF"
    )
    
    parser.add_argument(
        "-s", "--session",
        help="Nom de la session",
        default=None
    )
    
    parser.add_argument(
        "--install-alias",
        action="store_true",
        help="Installer les alias bash"
    )
    
    args = parser.parse_args()
    
    if args.install_alias:
        setup_bash_alias()
        return
    
    # Démarrer Gieokja
    try:
        wrapper = GieokjaWrapper(args.session)
        wrapper.start()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interruption détectée{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Erreur: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()