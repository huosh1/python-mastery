#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface REPL interactive pour Seullipeo
Style Metasploit avec commandes dynamiques
"""

import cmd
import sys
import os
import json
from datetime import datetime
from pathlib import Path

from utils.display import print_colored, show_banner
from utils.logger import get_logger
from utils.system import clear_screen
from exploits import get_available_modules, load_module

logger = get_logger(__name__)

class ModuleContext:
    """Contexte d'un module chargé"""
    
    def __init__(self, name, instance):
        self.name = name
        self.instance = instance
        self.scan_results = []
        self.options = {}
        self.notes = []
    
    def add_note(self, note):
        """Ajoute une note au module"""
        self.notes.append({
            'timestamp': datetime.now().isoformat(),
            'content': note
        })

class InteractiveShell(cmd.Cmd):
    """Shell interactif principal"""
    
    def __init__(self):
        super().__init__()
        self.intro = None
        self.current_module = None
        self.global_options = {
            'RHOST': None,
            'LHOST': None,
            'LPORT': '4444',
            'INTERFACE': 'eth0'
        }
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'commands_history': [],
            'modules_used': []
        }
        self.update_prompt()
    
    def update_prompt(self):
        """Met à jour le prompt selon le contexte"""
        if self.current_module:
            module_name = self.current_module.name
            self.prompt = print_colored(f"seullipeo[{module_name}]> ", "red", return_string=True)
        else:
            self.prompt = print_colored("seullipeo> ", "cyan", return_string=True)
    
    def cmdloop(self, intro=None):
        """Override pour gérer les interruptions clavier"""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            print_colored("\n[!] Utilisez 'exit' pour quitter", "yellow")
            self.cmdloop()
    
    def emptyline(self):
        """Ne fait rien sur ligne vide (évite de répéter la dernière commande)"""
        pass
    
    def default(self, line):
        """Gère les commandes non reconnues"""
        print_colored(f"[-] Commande inconnue: {line}", "red")
        print_colored("[*] Tapez 'help' pour voir les commandes disponibles", "blue")
    
    def precmd(self, line):
        """Appelé avant chaque commande - logging"""
        if line.strip():
            self.session_data['commands_history'].append({
                'timestamp': datetime.now().isoformat(),
                'command': line.strip(),
                'module': self.current_module.name if self.current_module else None
            })
        return line
    
    # ==================== COMMANDES GLOBALES ====================
    
    def do_banner(self, arg):
        """Affiche la bannière"""
        show_banner()
    
    def do_help(self, arg):
        """Affiche l'aide"""
        if not arg:
            print_colored("\n=== COMMANDES GLOBALES ===", "cyan")
            global_commands = [
                ("help", "Affiche cette aide"),
                ("banner", "Affiche la bannière ASCII"),
                ("list", "Liste tous les modules disponibles"),
                ("show modules", "Alias pour 'list'"),
                ("use <module>", "Charge un module"),
                ("set <var> <value>", "Définit une variable globale"),
                ("show options", "Affiche les variables globales"),
                ("clear", "Nettoie l'écran"),
                ("version", "Affiche la version"),
                ("save-session <name>", "Sauvegarde la session"),
                ("load-session <name>", "Charge une session"),
                ("history", "Affiche l'historique des commandes"),
                ("exit/quit", "Quitte le shell")
            ]
            
            for cmd, desc in global_commands:
                print_colored(f"  {cmd:<20} - {desc}", "white")
            
            if self.current_module:
                print_colored(f"\n=== COMMANDES MODULE [{self.current_module.name.upper()}] ===", "yellow")
                module_commands = [
                    ("info", "Affiche les infos du module"),
                    ("scan", "Lance un scan"),
                    ("list vulns", "Liste les vulnérabilités détectées"),
                    ("exploit <id>", "Lance un exploit spécifique"),
                    ("exploit all", "Lance tous les exploits"),
                    ("back", "Retourne au shell principal"),
                    ("notes", "Gère les notes du module"),
                    ("save", "Sauvegarde les résultats")
                ]
                
                for cmd, desc in module_commands:
                    print_colored(f"  {cmd:<20} - {desc}", "white")
        else:
            super().do_help(arg)
    
    def do_list(self, arg):
        """Liste tous les modules disponibles"""
        print_colored("\n[*] Modules disponibles:", "blue")
        modules = get_available_modules()
        
        for i, (module_name, module_info) in enumerate(modules.items(), 1):
            status = "✓" if module_info.get('available', True) else "✗"
            print_colored(f"  {i:2d}. {status} {module_name:<15} - {module_info.get('description', 'N/A')}", "white")
        
        print_colored(f"\n[*] Total: {len(modules)} modules", "green")
    
    def do_show(self, arg):
        """Commande show avec sous-commandes"""
        if arg == "modules":
            self.do_list("")
        elif arg == "options":
            print_colored("\n[*] Variables globales:", "blue")
            for var, value in self.global_options.items():
                display_value = value if value else "<non défini>"
                print_colored(f"  {var:<12} = {display_value}", "white")
            
            if self.current_module and self.current_module.options:
                print_colored(f"\n[*] Variables du module [{self.current_module.name}]:", "yellow")
                for var, value in self.current_module.options.items():
                    display_value = value if value else "<non défini>"
                    print_colored(f"  {var:<12} = {display_value}", "white")
        else:
            print_colored("[-] Usage: show [modules|options]", "red")
    
    def do_use(self, arg):
        """Charge un module"""
        if not arg:
            print_colored("[-] Usage: use <module_name>", "red")
            return
        
        module_name = arg.strip()
        
        print_colored(f"[*] Chargement du module: {module_name}", "blue")
        
        try:
            module = load_module(module_name)
            if not module:
                print_colored(f"[-] Module '{module_name}' non trouvé", "red")
                return
            
            # Création de l'instance
            instance = module.Module()
            self.current_module = ModuleContext(module_name, instance)
            
            # Ajout à l'historique
            if module_name not in self.session_data['modules_used']:
                self.session_data['modules_used'].append(module_name)
            
            self.update_prompt()
            print_colored(f"[+] Module '{module_name}' chargé avec succès", "green")
            
            # Affichage automatique des infos
            self.do_info("")
            
        except Exception as e:
            print_colored(f"[-] Erreur lors du chargement: {str(e)}", "red")
            logger.error(f"Erreur chargement module {module_name}: {e}")
    
    def do_set(self, arg):
        """Définit une variable"""
        if not arg or len(arg.split()) < 2:
            print_colored("[-] Usage: set <variable> <valeur>", "red")
            return
        
        parts = arg.split(maxsplit=1)
        var_name = parts[0].upper()
        var_value = parts[1]
        
        # Variable globale ou du module
        if self.current_module and hasattr(self.current_module.instance, 'options'):
            if var_name in self.current_module.instance.options:
                self.current_module.options[var_name] = var_value
                print_colored(f"[+] {var_name} => {var_value} (module)", "green")
                return
        
        # Variable globale
        if var_name in self.global_options:
            self.global_options[var_name] = var_value
            print_colored(f"[+] {var_name} => {var_value} (global)", "green")
        else:
            print_colored(f"[-] Variable inconnue: {var_name}", "red")
    
    def do_clear(self, arg):
        """Nettoie l'écran"""
        clear_screen()
    
    def do_version(self, arg):
        """Affiche la version"""
        print_colored("Seullipeo v1.0.0", "cyan")
        print_colored("Framework d'escalade de privilèges Linux", "white")
    
    def do_history(self, arg):
        """Affiche l'historique des commandes"""
        print_colored("\n[*] Historique des commandes:", "blue")
        for i, entry in enumerate(self.session_data['commands_history'][-20:], 1):
            module = f"[{entry['module']}]" if entry['module'] else "[global]"
            print_colored(f"  {i:2d}. {module:<12} {entry['command']}", "white")
    
    def do_exit(self, arg):
        """Quitte le shell"""
        print_colored("\n[*] Au revoir !", "cyan")
        return True
    
    def do_quit(self, arg):
        """Alias pour exit"""
        return self.do_exit(arg)
    
    # ==================== COMMANDES MODULE ====================
    
    def do_info(self, arg):
        """Affiche les informations du module courant"""
        if not self.current_module:
            print_colored("[-] Aucun module chargé", "red")
            return
        
        instance = self.current_module.instance
        
        print_colored(f"\n=== MODULE: {self.current_module.name.upper()} ===", "cyan")
        print_colored(f"Description: {getattr(instance, 'description', 'N/A')}", "white")
        print_colored(f"Auteur: {getattr(instance, 'author', 'N/A')}", "white")
        print_colored(f"Risque: {getattr(instance, 'risk_level', 'N/A')}", "white")
        
        if hasattr(instance, 'targets'):
            print_colored(f"Cibles: {', '.join(instance.targets)}", "white")
        
        # Options du module
        if hasattr(instance, 'options') and instance.options:
            print_colored("\nOptions:", "yellow")
            for opt, desc in instance.options.items():
                value = self.current_module.options.get(opt, "<non défini>")
                print_colored(f"  {opt:<15} = {value:<20} ({desc})", "white")
        
        # Statistiques
        vuln_count = len(self.current_module.scan_results)
        note_count = len(self.current_module.notes)
        print_colored(f"\nStatistiques:", "yellow")
        print_colored(f"  Vulnérabilités trouvées: {vuln_count}", "white")
        print_colored(f"  Notes: {note_count}", "white")
    
    def do_scan(self, arg):
        """Lance un scan avec le module courant"""
        if not self.current_module:
            print_colored("[-] Aucun module chargé", "red")
            return
        
        print_colored(f"[*] Scan en cours avec {self.current_module.name}...", "yellow")
        
        try:
            results = self.current_module.instance.scan()
            self.current_module.scan_results = results
            
            if results:
                print_colored(f"[+] {len(results)} vulnérabilité(s) trouvée(s)", "green")
                for i, vuln in enumerate(results, 1):
                    desc = vuln.get('description', 'N/A')
                    path = vuln.get('path', '')
                    risk = vuln.get('risk', 'Unknown')
                    print_colored(f"  {i}. [{risk}] {desc}", "white")
                    if path:
                        print_colored(f"     Chemin: {path}", "cyan")
            else:
                print_colored("[-] Aucune vulnérabilité trouvée", "yellow")
                
        except Exception as e:
            print_colored(f"[-] Erreur lors du scan: {str(e)}", "red")
            logger.error(f"Erreur scan {self.current_module.name}: {e}")
    
    def do_exploit(self, arg):
        """Lance un ou plusieurs exploits"""
        if not self.current_module:
            print_colored("[-] Aucun module chargé", "red")
            return
        
        if not self.current_module.scan_results:
            print_colored("[-] Aucune vulnérabilité détectée. Lancez d'abord 'scan'", "red")
            return
        
        if not arg:
            print_colored("[-] Usage: exploit <id|all>", "red")
            return
        
        try:
            if arg.lower() == "all":
                print_colored("[*] Lancement de tous les exploits...", "yellow")
                results = self.current_module.instance.exploit_all()
                
                success_count = sum(1 for r in results if r.get('success', False))
                print_colored(f"[*] Résultats: {success_count}/{len(results)} exploits réussis", "blue")
                
                for i, result in enumerate(results, 1):
                    status = "✓" if result.get('success', False) else "✗"
                    desc = result.get('description', 'N/A')
                    print_colored(f"  {i}. {status} {desc}", "green" if result.get('success') else "red")
                    
                    if result.get('output'):
                        print_colored(f"     Output: {result['output'][:100]}...", "cyan")
            
            else:
                # Exploit spécifique par ID
                try:
                    exploit_id = int(arg) - 1
                    if 0 <= exploit_id < len(self.current_module.scan_results):
                        vuln = self.current_module.scan_results[exploit_id]
                        print_colored(f"[*] Exploitation de: {vuln.get('description', 'N/A')}", "yellow")
                        
                        result = self.current_module.instance.exploit_single(vuln)
                        
                        if result.get('success', False):
                            print_colored("[+] Exploit réussi !", "green")
                            if result.get('output'):
                                print_colored(f"Output: {result['output']}", "cyan")
                        else:
                            print_colored("[-] Exploit échoué", "red")
                            if result.get('error'):
                                print_colored(f"Erreur: {result['error']}", "red")
                    else:
                        print_colored(f"[-] ID invalide. Utilisez 1-{len(self.current_module.scan_results)}", "red")
                        
                except ValueError:
                    print_colored("[-] ID doit être un nombre", "red")
                    
        except Exception as e:
            print_colored(f"[-] Erreur lors de l'exploitation: {str(e)}", "red")
            logger.error(f"Erreur exploit {self.current_module.name}: {e}")
    
    def do_vulns(self, arg):
        """Alias pour 'list vulns'"""
        if arg == "":
            arg = "vulns"
        
        if arg == "vulns":
            if not self.current_module:
                print_colored("[-] Aucun module chargé", "red")
                return
            
            if not self.current_module.scan_results:
                print_colored("[-] Aucune vulnérabilité. Lancez d'abord 'scan'", "yellow")
                return
            
            print_colored(f"\n[*] Vulnérabilités détectées ({len(self.current_module.scan_results)}):", "blue")
            for i, vuln in enumerate(self.current_module.scan_results, 1):
                desc = vuln.get('description', 'N/A')
                path = vuln.get('path', '')
                risk = vuln.get('risk', 'Unknown')
                
                print_colored(f"  {i:2d}. [{risk}] {desc}", "white")
                if path:
                    print_colored(f"      Chemin: {path}", "cyan")
                if vuln.get('details'):
                    print_colored(f"      Détails: {vuln['details']}", "yellow")
    
    def do_back(self, arg):
        """Retourne au shell principal"""
        if self.current_module:
            print_colored(f"[*] Sortie du module: {self.current_module.name}", "blue")
            self.current_module = None
            self.update_prompt()
        else:
            print_colored("[-] Déjà dans le shell principal", "yellow")
    
    def do_notes(self, arg):
        """Gère les notes du module"""
        if not self.current_module:
            print_colored("[-] Aucun module chargé", "red")
            return
        
        if not arg:
            # Affiche les notes
            if self.current_module.notes:
                print_colored(f"\n[*] Notes pour {self.current_module.name}:", "blue")
                for i, note in enumerate(self.current_module.notes, 1):
                    timestamp = note['timestamp'][:19]  # Format: YYYY-MM-DD HH:MM:SS
                    print_colored(f"  {i}. [{timestamp}] {note['content']}", "white")
            else:
                print_colored("[-] Aucune note pour ce module", "yellow")
        else:
            # Ajoute une note
            self.current_module.add_note(arg)
            print_colored("[+] Note ajoutée", "green")
    
    def do_save(self, arg):
        """Sauvegarde les résultats du module"""
        if not self.current_module:
            print_colored("[-] Aucun module chargé", "red")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = arg if arg else f"output/{self.current_module.name}_{timestamp}.json"
        
        # Création du répertoire si nécessaire
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'module': self.current_module.name,
            'timestamp': timestamp,
            'scan_results': self.current_module.scan_results,
            'options': self.current_module.options,
            'notes': self.current_module.notes
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print_colored(f"[+] Résultats sauvegardés dans: {filename}", "green")
            
        except Exception as e:
            print_colored(f"[-] Erreur sauvegarde: {str(e)}", "red")
    
    # ==================== GESTION DES SESSIONS ====================
    
    def do_save_session(self, arg):
        """Sauvegarde la session courante"""
        if not arg:
            arg = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_file = f"sessions/session_{arg}.json"
        Path("sessions").mkdir(exist_ok=True)
        
        session_data = {
            **self.session_data,
            'end_time': datetime.now().isoformat(),
            'global_options': self.global_options,
            'current_module': self.current_module.name if self.current_module else None
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print_colored(f"[+] Session sauvegardée: {session_file}", "green")
            
        except Exception as e:
            print_colored(f"[-] Erreur sauvegarde session: {str(e)}", "red")
    
    def do_load_session(self, arg):
        """Charge une session précédente"""
        if not arg:
            # Liste les sessions disponibles
            sessions_dir = Path("sessions")
            if sessions_dir.exists():
                sessions = list(sessions_dir.glob("session_*.json"))
                if sessions:
                    print_colored("\n[*] Sessions disponibles:", "blue")
                    for i, session in enumerate(sessions, 1):
                        name = session.stem.replace("session_", "")
                        print_colored(f"  {i}. {name}", "white")
                else:
                    print_colored("[-] Aucune session sauvegardée", "yellow")
            else:
                print_colored("[-] Répertoire sessions non trouvé", "yellow")
            return
        
        session_file = f"sessions/session_{arg}.json"
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restauration des données
            self.global_options.update(session_data.get('global_options', {}))
            self.session_data['commands_history'] = session_data.get('commands_history', [])
            
            print_colored(f"[+] Session '{arg}' chargée", "green")
            
            # Rechargement du dernier module si spécifié
            if session_data.get('current_module'):
                self.do_use(session_data['current_module'])
                
        except FileNotFoundError:
            print_colored(f"[-] Session '{arg}' non trouvée", "red")
        except Exception as e:
            print_colored(f"[-] Erreur chargement session: {str(e)}", "red")
    
    def run(self):
        """Lance le shell interactif"""
        print_colored("\n[*] Shell interactif Seullipeo", "cyan")
        print_colored("[*] Tapez 'help' pour voir les commandes disponibles", "blue")
        print_colored("[*] Utilisez 'list' pour voir les modules", "blue")
        print("")
        
        try:
            self.cmdloop()
        except Exception as e:
            print_colored(f"[-] Erreur shell: {str(e)}", "red")
            logger.error(f"Erreur shell: {e}")

# Pour utilisation standalone
if __name__ == "__main__":
    shell = InteractiveShell()
    shell.run()