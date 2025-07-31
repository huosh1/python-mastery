"""
Interface CLI pour Gieokja
"""

import os
import sys
import cmd
import readline
from datetime import datetime
from pathlib import Path

from utils.colors import Colors
from utils.logger import get_logger


class GieokjaCLI(cmd.Cmd):
    """Interface en ligne de commande pour Gieokja"""
    
    intro = f"{Colors.CYAN}Gieokja CLI - Tapez 'help' ou '?' pour la liste des commandes.{Colors.RESET}"
    prompt = f"{Colors.GREEN}gieokja> {Colors.RESET}"
    
    def __init__(self, tracker, writer):
        super().__init__()
        self.tracker = tracker
        self.writer = writer
        self.logger = get_logger()
        
        # Configuration de l'historique
        self.history_file = os.path.expanduser('~/.gieokja_history')
        self._setup_history()
        
        # État de la CLI
        self.last_command_output = None
    
    def _setup_history(self):
        """Configurer l'historique des commandes"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        
        readline.set_history_length(1000)
    
    def save_history(self):
        """Sauvegarder l'historique"""
        readline.write_history_file(self.history_file)
    
    def do_exec(self, command):
        """Exécuter une commande système et la tracker
        Usage: exec <commande>"""
        if not command:
            print(f"{Colors.RED}Usage: exec <commande>{Colors.RESET}")
            return
        
        print(f"{Colors.YELLOW}Exécution: {command}{Colors.RESET}")
        output = self.tracker.execute_and_track(command)
        
        if output:
            print(output)
            self.last_command_output = output
    
    def do_note(self, note):
        """Ajouter une note à la session
        Usage: note <texte de la note>"""
        if not note:
            print(f"{Colors.RED}Usage: note <texte de la note>{Colors.RESET}")
            return
        
        self.tracker.add_note(note)
        print(f"{Colors.GREEN}✓ Note ajoutée{Colors.RESET}")
    
    def do_flag(self, flag_text):
        """Marquer un flag (ou extraire de la dernière sortie)
        Usage: flag [texte du flag]"""
        if flag_text:
            self.tracker.mark_as_flag(flag_text)
        else:
            self.tracker.mark_as_flag()
        
        print(f"{Colors.GREEN}✓ Flag marqué{Colors.RESET}")
    
    def do_todo(self, todo):
        """Ajouter un TODO
        Usage: todo <description>"""
        if not todo:
            print(f"{Colors.RED}Usage: todo <description>{Colors.RESET}")
            return
        
        self.tracker.add_todo(todo)
        print(f"{Colors.GREEN}✓ TODO ajouté{Colors.RESET}")
    
    def do_save(self, _):
        """Forcer la sauvegarde du write-up"""
        session_data = self.tracker.get_session_data()
        self.writer.write_session_data(session_data)
        print(f"{Colors.GREEN}✓ Write-up sauvegardé: {self.writer.output_path}{Colors.RESET}")
    
    def do_status(self, _):
        """Afficher le statut de la session actuelle"""
        data = self.tracker.get_session_data()
        
        print(f"\n{Colors.CYAN}=== Statut de la session ==={Colors.RESET}")
        print(f"Session: {Colors.WHITE}{data['session_name']}{Colors.RESET}")
        print(f"Utilisateur: {Colors.WHITE}{data['current_user']}@{data['current_host']}{Colors.RESET}")
        
        if self.tracker.target_ip:
            print(f"Cible: {Colors.WHITE}{self.tracker.target_ip}{Colors.RESET}")
        
        print(f"\nStatistiques:")
        print(f"  • Commandes: {Colors.YELLOW}{len(data['commands'])}{Colors.RESET}")
        print(f"  • Flags: {Colors.GREEN}{len(data['flags'])}{Colors.RESET}")
        print(f"  • Notes: {Colors.BLUE}{len(data['notes'])}{Colors.RESET}")
        print(f"  • TODOs: {Colors.MAGENTA}{len(data['todos'])}{Colors.RESET}")
        
        print(f"\nFichier: {Colors.WHITE}{self.writer.output_path}{Colors.RESET}")
    
    def do_show(self, what):
        """Afficher des éléments spécifiques
        Usage: show [flags|notes|todos|commands]"""
        data = self.tracker.get_session_data()
        
        if what == 'flags' or not what:
            if data['flags']:
                print(f"\n{Colors.GREEN}=== Flags trouvés ==={Colors.RESET}")
                for i, flag in enumerate(data['flags'], 1):
                    print(f"{i}. {Colors.YELLOW}{flag['flag']}{Colors.RESET}")
                    print(f"   Trouvé à: {flag['timestamp'].strftime('%H:%M:%S')}")
                    if flag.get('command'):
                        print(f"   Commande: {flag['command'][:60]}...")
            else:
                print(f"{Colors.YELLOW}Aucun flag trouvé.{Colors.RESET}")
        
        if what == 'notes':
            if data['notes']:
                print(f"\n{Colors.BLUE}=== Notes ==={Colors.RESET}")
                for note in data['notes']:
                    print(f"• [{note['timestamp'].strftime('%H:%M:%S')}] {note['note']}")
            else:
                print(f"{Colors.YELLOW}Aucune note.{Colors.RESET}")
        
        if what == 'todos':
            if data['todos']:
                print(f"\n{Colors.MAGENTA}=== TODOs ==={Colors.RESET}")
                for todo in data['todos']:
                    status = "✓" if todo.get('completed') else "○"
                    print(f"{status} {todo['todo']}")
            else:
                print(f"{Colors.YELLOW}Aucun TODO.{Colors.RESET}")
        
        if what == 'commands':
            if data['commands']:
                print(f"\n{Colors.CYAN}=== Dernières commandes ==={Colors.RESET}")
                # Afficher les 10 dernières commandes
                for cmd in data['commands'][-10:]:
                    timestamp = cmd['timestamp'].strftime('%H:%M:%S')
                    important = "⭐" if cmd.get('important') else " "
                    print(f"{important}[{timestamp}] {cmd['command']}")
            else:
                print(f"{Colors.YELLOW}Aucune commande.{Colors.RESET}")
    
    def do_target(self, ip):
        """Définir l'IP cible
        Usage: target <ip>"""
        if not ip:
            if self.tracker.target_ip:
                print(f"Cible actuelle: {Colors.WHITE}{self.tracker.target_ip}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}Aucune cible définie.{Colors.RESET}")
        else:
            self.tracker.target_ip = ip
            print(f"{Colors.GREEN}✓ Cible définie: {ip}{Colors.RESET}")
    
    def do_shell(self, command):
        """Exécuter une commande shell directement (alias: !)
        Usage: shell <commande> ou !<commande>"""
        self.do_exec(command)
    
    def do_exit(self, _):
        """Quitter Gieokja"""
        print(f"{Colors.YELLOW}Arrêt de Gieokja...{Colors.RESET}")
        self.save_history()
        return True
    
    def do_quit(self, arg):
        """Quitter Gieokja (alias pour exit)"""
        return self.do_exit(arg)
    
    def do_clear(self, _):
        """Effacer l'écran"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def do_help(self, arg):
        """Afficher l'aide"""
        if arg:
            # Aide spécifique à une commande
            super().do_help(arg)
        else:
            # Aide générale
            print(f"\n{Colors.CYAN}=== Commandes Gieokja ==={Colors.RESET}")
            print(f"\n{Colors.WHITE}Tracking:{Colors.RESET}")
            print("  exec <cmd>    - Exécuter et tracker une commande")
            print("  !<cmd>        - Raccourci pour exec")
            print("  note <text>   - Ajouter une note")
            print("  flag [text]   - Marquer un flag")
            print("  todo <text>   - Ajouter un TODO")
            print("  save          - Sauvegarder le write-up")
            
            print(f"\n{Colors.WHITE}Affichage:{Colors.RESET}")
            print("  status        - Statut de la session")
            print("  show <type>   - Afficher (flags/notes/todos/commands)")
            print("  target [ip]   - Afficher/définir la cible")
            
            print(f"\n{Colors.WHITE}Système:{Colors.RESET}")
            print("  clear         - Effacer l'écran")
            print("  help [cmd]    - Afficher l'aide")
            print("  exit/quit     - Quitter Gieokja")
            
            print(f"\n{Colors.BLUE}Raccourcis CLI:{Colors.RESET}")
            print("  Les commandes internes peuvent être préfixées par !")
            print("  Ex: !note, !flag, !todo, !save")
    
    def default(self, line):
        """Gérer les commandes non reconnues"""
        # Si la ligne commence par !, traiter comme une commande shell
        if line.startswith('!'):
            # Vérifier si c'est une commande interne
            parts = line[1:].split(maxsplit=1)
            if parts:
                cmd_name = parts[0]
                args = parts[1] if len(parts) > 1 else ''
                
                # Mapper vers les commandes internes
                if cmd_name in ['note', 'flag', 'todo', 'save']:
                    method = getattr(self, f'do_{cmd_name}', None)
                    if method:
                        method(args)
                        return
            
            # Sinon, exécuter comme commande shell
            self.do_exec(line[1:])
        else:
            # Essayer d'exécuter comme commande système
            self.do_exec(line)
    
    def emptyline(self):
        """Ne rien faire sur une ligne vide"""
        pass
    
    def precmd(self, line):
        """Pré-traitement de la commande"""
        # Enregistrer la commande dans l'historique interne
        if line and not line.startswith(('help', 'status', 'show', 'clear')):
            self.logger.debug(f"Commande CLI: {line}")
        return line
    
    def postcmd(self, stop, line):
        """Post-traitement de la commande"""
        # Sauvegarder automatiquement après certaines commandes
        if line.startswith(('note', 'flag', 'todo')):
            session_data = self.tracker.get_session_data()
            self.writer.write_session_data(session_data)
        return stop