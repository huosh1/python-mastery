"""
Module de tracking des commandes et événements
"""

import os
import re
import subprocess
import threading
import time
from datetime import datetime
from collections import deque
from pathlib import Path
import configparser

from utils.logger import get_logger
from utils.colors import Colors


class CommandTracker:
    """Classe pour tracker les commandes et événements"""
    
    def __init__(self, session_name):
        self.session_name = session_name
        self.logger = get_logger()
        self.config = self._load_config()
        
        # Historique des commandes
        self.command_history = deque(maxlen=1000)
        self.last_command = None
        self.last_output = None
        
        # État de la session
        self.current_user = os.getenv("USER", "unknown")
        self.current_host = os.uname().nodename
        self.current_directory = os.getcwd()
        self.target_ip = None
        
        # Flags et notes
        self.flags_found = []
        self.notes = []
        self.todos = []
        
        # Thread de sauvegarde automatique
        self.running = False
        self.save_thread = None
        
        # Patterns de détection
        self._compile_patterns()
    
    def _load_config(self):
        """Charger la configuration"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config
    
    def _compile_patterns(self):
        """Compiler les patterns regex"""
        # Patterns de flags
        flag_patterns = self.config.get('tracking', 'flag_patterns', fallback='').split(', ')
        self.flag_regex = re.compile('|'.join(flag_patterns))
        
        # Commandes importantes
        self.important_commands = self.config.get('tracking', 'important_commands', fallback='').split(', ')
        
        # Commandes à ignorer
        self.ignore_commands = self.config.get('tracking', 'ignore_commands', fallback='').split(', ')
    
    def start(self):
        """Démarrer le tracking"""
        self.running = True
        self.logger.info(f"Tracking démarré pour la session: {self.session_name}")
        
        # Démarrer le thread de sauvegarde automatique
        interval = self.config.getint('general', 'auto_save_interval', fallback=30)
        self.save_thread = threading.Thread(target=self._auto_save_loop, args=(interval,))
        self.save_thread.daemon = True
        self.save_thread.start()
    
    def stop(self):
        """Arrêter le tracking"""
        self.running = False
        if self.save_thread:
            self.save_thread.join(timeout=5)
        self.logger.info("Tracking arrêté")
    
    def track_command(self, command, output=None):
        """Enregistrer une commande et sa sortie"""
        # Ignorer les commandes dans la liste d'exclusion
        cmd_base = command.split()[0] if command else ""
        if cmd_base in self.ignore_commands:
            return
        
        # Créer l'entrée de commande
        entry = {
            'timestamp': datetime.now(),
            'command': command,
            'output': output,
            'user': self.current_user,
            'host': self.current_host,
            'directory': self.current_directory,
            'important': self._is_important_command(command),
            'category': self._categorize_command(command)
        }
        
        # Ajouter à l'historique
        self.command_history.append(entry)
        self.last_command = command
        self.last_output = output
        
        # Détecter les flags dans la sortie
        if output:
            self._detect_flags(output)
        
        # Détecter les changements d'état
        self._detect_state_changes(command, output)
        
        self.logger.debug(f"Commande trackée: {command[:50]}...")
    
    def add_note(self, note):
        """Ajouter une note"""
        self.notes.append({
            'timestamp': datetime.now(),
            'note': note,
            'related_command': self.last_command
        })
        self.logger.info(f"Note ajoutée: {note}")
    
    def add_todo(self, todo):
        """Ajouter un TODO"""
        self.todos.append({
            'timestamp': datetime.now(),
            'todo': todo,
            'completed': False
        })
        self.logger.info(f"TODO ajouté: {todo}")
    
    def mark_as_flag(self, flag_text=None):
        """Marquer quelque chose comme un flag"""
        if flag_text:
            self.flags_found.append({
                'timestamp': datetime.now(),
                'flag': flag_text,
                'command': self.last_command
            })
        elif self.last_output:
            # S'assurer que last_output est une string
            output = str(self.last_output) if self.last_output else ""
            # Essayer d'extraire un flag de la dernière sortie
            matches = self.flag_regex.findall(output)
            for match in matches:
                self.flags_found.append({
                    'timestamp': datetime.now(),
                    'flag': match,
                    'command': self.last_command
                })
        
        self.logger.info(f"Flag marqué: {len(self.flags_found)} flags trouvés")
    
    def get_session_data(self):
        """Obtenir toutes les données de la session"""
        return {
            'session_name': self.session_name,
            'start_time': self.command_history[0]['timestamp'] if self.command_history else datetime.now(),
            'current_user': self.current_user,
            'current_host': self.current_host,
            'target_ip': self.target_ip,
            'commands': list(self.command_history),
            'flags': self.flags_found,
            'notes': self.notes,
            'todos': self.todos
        }
    
    def _is_important_command(self, command):
        """Vérifier si une commande est importante"""
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return False
        
        for important_cmd in self.important_commands:
            if important_cmd in cmd_parts[0]:
                return True
        return False
    
    def _categorize_command(self, command):
        """Catégoriser une commande"""
        cmd_lower = command.lower()
        
        # Vérifier chaque catégorie
        categories = ['privilege_escalation', 'reconnaissance', 'web_enumeration', 'exploitation', 'post_exploitation']
        
        for category in categories:
            patterns = self.config.get('tracking', category, fallback='').split(', ')
            for pattern in patterns:
                if pattern and pattern in cmd_lower:
                    return category.replace('_', ' ').title()
        
        return "Général"
    
    def _detect_flags(self, output):
        """Détecter automatiquement les flags dans la sortie"""
        if not output or output is None:
            return
        
        # S'assurer que output est une string
        output = str(output)
        
        matches = self.flag_regex.findall(output)
        for match in matches:
            # Vérifier si ce flag n'est pas déjà enregistré
            if not any(f['flag'] == match for f in self.flags_found):
                self.flags_found.append({
                    'timestamp': datetime.now(),
                    'flag': match,
                    'command': self.last_command,
                    'auto_detected': True
                })
                print(f"{Colors.GREEN}🏁 Flag détecté: {match}{Colors.RESET}")
    
    def _detect_state_changes(self, command, output):
        """Détecter les changements d'état (user, host, directory)"""
        # Changement d'utilisateur
        if command.startswith(('su ', 'sudo su', 'sudo -i')):
            # TODO: Parser la sortie pour détecter le nouvel utilisateur
            pass
        
        # Changement de répertoire
        if command.startswith('cd '):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                try:
                    new_dir = os.path.expanduser(parts[1])
                    if os.path.isabs(new_dir):
                        self.current_directory = new_dir
                    else:
                        self.current_directory = os.path.join(self.current_directory, new_dir)
                except:
                    pass
        
        # Détection d'IP cible
        if command.startswith(('nmap ', 'ping ', 'ssh ')):
            # Extraire l'IP avec regex
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            matches = re.findall(ip_pattern, command)
            if matches and not matches[0].startswith('127.'):
                self.target_ip = matches[0]
    
    def _auto_save_loop(self, interval):
        """Boucle de sauvegarde automatique"""
        while self.running:
            time.sleep(interval)
            # La sauvegarde sera gérée par le WriteupWriter
            self.logger.debug("Auto-save triggered")
    
    def execute_and_track(self, command):
        """Exécuter une commande et tracker le résultat"""
        try:
            # Exécuter la commande
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n{Colors.RED}STDERR:{Colors.RESET}\n{result.stderr}"
            
            # Tracker la commande
            self.track_command(command, output)
            
            return output
            
        except subprocess.TimeoutExpired:
            error_msg = f"Commande timeout après 30 secondes"
            self.track_command(command, error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            self.track_command(command, error_msg)
            return error_msg