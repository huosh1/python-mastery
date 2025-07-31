"""
Système de hooks et d'écouteurs pour déclenchement automatique
"""

import os
import re
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable

from utils.logger import get_logger


class Hook(ABC):
    """Classe de base pour les hooks"""
    
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.logger = get_logger()
    
    @abstractmethod
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """Déterminer si le hook doit se déclencher"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Exécuter l'action du hook"""
        pass


class CommandHook(Hook):
    """Hook déclenché par des commandes spécifiques"""
    
    def __init__(self, name: str, patterns: List[str], action: Callable):
        super().__init__(name)
        self.patterns = [re.compile(p) for p in patterns]
        self.action = action
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        command = context.get('command', '')
        return any(pattern.search(command) for pattern in self.patterns)
    
    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)


class OutputHook(Hook):
    """Hook déclenché par des patterns dans la sortie"""
    
    def __init__(self, name: str, patterns: List[str], action: Callable):
        super().__init__(name)
        self.patterns = [re.compile(p) for p in patterns]
        self.action = action
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        output = context.get('output', '')
        return any(pattern.search(output) for pattern in self.patterns)
    
    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)


class StateChangeHook(Hook):
    """Hook déclenché par des changements d'état"""
    
    def __init__(self, name: str, state_key: str, action: Callable):
        super().__init__(name)
        self.state_key = state_key
        self.action = action
        self.previous_value = None
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        current_value = context.get(self.state_key)
        if current_value != self.previous_value:
            self.previous_value = current_value
            return True
        return False
    
    def execute(self, context: Dict[str, Any]) -> Any:
        return self.action(context)


class HookManager:
    """Gestionnaire de hooks"""
    
    def __init__(self):
        self.hooks: List[Hook] = []
        self.logger = get_logger()
        self._setup_default_hooks()
    
    def _setup_default_hooks(self):
        """Configurer les hooks par défaut"""
        
        # Hook pour détecter les changements d'IP
        self.add_hook(CommandHook(
            "ip_detection",
            [r"nmap\s+[\d\.]+", r"ping\s+[\d\.]+", r"ssh\s+.*@[\d\.]+"],
            self._detect_target_ip
        ))
        
        # Hook pour détecter l'obtention d'un shell
        self.add_hook(OutputHook(
            "shell_detection",
            [r"\$\s*$", r"#\s*$", r".*@.*:.*[\$#]\s*$"],
            self._detect_shell_access
        ))
        
        # Hook pour détecter les élévations de privilèges
        self.add_hook(CommandHook(
            "privesc_detection",
            [r"sudo\s+-l", r"su\s+-", r"sudo\s+su", r"chmod\s+\+s"],
            self._detect_privilege_escalation
        ))
        
        # Hook pour détecter les services web
        self.add_hook(OutputHook(
            "web_service_detection",
            [r"80/tcp\s+open", r"443/tcp\s+open", r"8080/tcp\s+open", r"HTTP/"],
            self._detect_web_service
        ))
        
        # Hook pour auto-sauvegarder après certaines commandes
        self.add_hook(CommandHook(
            "auto_save_trigger",
            [r"cat\s+.*\.txt", r"whoami", r"id", r"uname", r"systeminfo"],
            self._trigger_auto_save
        ))
    
    def add_hook(self, hook: Hook):
        """Ajouter un hook"""
        self.hooks.append(hook)
        self.logger.debug(f"Hook ajouté: {hook.name}")
    
    def remove_hook(self, name: str):
        """Retirer un hook"""
        self.hooks = [h for h in self.hooks if h.name != name]
    
    def process(self, context: Dict[str, Any]) -> List[Any]:
        """Traiter tous les hooks avec le contexte donné"""
        results = []
        
        for hook in self.hooks:
            if hook.enabled and hook.should_trigger(context):
                try:
                    result = hook.execute(context)
                    if result:
                        results.append(result)
                    self.logger.debug(f"Hook exécuté: {hook.name}")
                except Exception as e:
                    self.logger.error(f"Erreur dans le hook {hook.name}: {e}")
        
        return results
    
    # Actions des hooks par défaut
    
    def _detect_target_ip(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Détecter l'IP cible dans une commande"""
        command = context.get('command', '')
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        matches = re.findall(ip_pattern, command)
        
        if matches:
            # Filtrer les IPs locales
            target_ips = [ip for ip in matches if not ip.startswith(('127.', '0.'))]
            if target_ips:
                return {
                    'type': 'target_ip_detected',
                    'ip': target_ips[0],
                    'message': f"IP cible détectée: {target_ips[0]}"
                }
        return None
    
    def _detect_shell_access(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Détecter l'obtention d'un shell"""
        output = context.get('output', '')
        
        # Patterns de prompts shell
        shell_patterns = [
            (r".*@.*:.*[\$#]\s*$", "Shell Unix/Linux détecté"),
            (r"C:\\.*>", "Shell Windows détecté"),
            (r"PS\s+.*>", "PowerShell détecté"),
            (r"meterpreter\s*>", "Meterpreter détecté")
        ]
        
        for pattern, message in shell_patterns:
            if re.search(pattern, output, re.MULTILINE):
                return {
                    'type': 'shell_access',
                    'message': message
                }
        return None
    
    def _detect_privilege_escalation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Détecter une tentative d'élévation de privilèges"""
        command = context.get('command', '')
        
        return {
            'type': 'privilege_escalation_attempt',
            'command': command,
            'message': f"Tentative d'élévation de privilèges: {command.split()[0]}"
        }
    
    def _detect_web_service(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Détecter un service web"""
        output = context.get('output', '')
        
        # Extraire les ports web
        web_ports = []
        port_pattern = r'(\d+)/tcp\s+open\s+.*http'
        matches = re.findall(port_pattern, output, re.IGNORECASE)
        
        if matches:
            web_ports = list(set(matches))
            return {
                'type': 'web_service_found',
                'ports': web_ports,
                'message': f"Services web détectés sur les ports: {', '.join(web_ports)}"
            }
        return None
    
    def _trigger_auto_save(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Déclencher une sauvegarde automatique"""
        return {
            'type': 'auto_save_requested',
            'reason': 'Commande importante exécutée'
        }


class BashIntegration:
    """Intégration avec Bash pour capturer les commandes"""
    
    @staticmethod
    def generate_bash_hook():
        """Générer le code bash pour l'intégration"""
        return '''
# Gieokja Bash Integration
export GIEOKJA_SESSION="${GIEOKJA_SESSION:-default}"

gieokja_preexec() {
    # Capturer la commande avant exécution
    echo "$1" > /tmp/gieokja_last_command_$$.txt
}

gieokja_precmd() {
    # Capturer après l'exécution
    local last_command=$(cat /tmp/gieokja_last_command_$$.txt 2>/dev/null)
    if [ ! -z "$last_command" ]; then
        # Envoyer la commande à Gieokja via un fichier ou socket
        echo "[$PWD] $last_command" >> ~/.gieokja/commands.log
        rm -f /tmp/gieokja_last_command_$$.txt
    fi
}

# Configurer les hooks selon le shell
if [ -n "$BASH_VERSION" ]; then
    # Bash
    trap 'gieokja_preexec "$BASH_COMMAND"' DEBUG
    PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND; }gieokja_precmd"
elif [ -n "$ZSH_VERSION" ]; then
    # Zsh
    preexec() { gieokja_preexec "$1" }
    precmd() { gieokja_precmd }
fi

# Alias pour les commandes Gieokja
alias !note='gieokja note'
alias !flag='gieokja flag'
alias !todo='gieokja todo'
alias !save='gieokja save'
'''
    
    @staticmethod
    def install():
        """Installer l'intégration bash"""
        hook_code = BashIntegration.generate_bash_hook()
        
        # Déterminer le fichier de configuration shell
        shell = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell:
            rc_file = os.path.expanduser('~/.zshrc')
        else:
            rc_file = os.path.expanduser('~/.bashrc')
        
        # Vérifier si déjà installé
        marker = "# Gieokja Bash Integration"
        try:
            with open(rc_file, 'r') as f:
                if marker in f.read():
                    print("L'intégration Gieokja est déjà installée.")
                    return False
        except FileNotFoundError:
            pass
        
        # Ajouter le hook
        with open(rc_file, 'a') as f:
            f.write(f"\n{hook_code}\n")
        
        print(f"Intégration Gieokja installée dans {rc_file}")
        print("Rechargez votre shell ou exécutez: source " + rc_file)
        return True