#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système de logging pour Seullipeo
Configuration centralisée des logs
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuration globale
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Fichiers de log
LOG_DIR = 'logs'
LOG_FILE = 'seullipeo.log'
ERROR_LOG_FILE = 'seullipeo_errors.log'

# Taille max des fichiers de log (10MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
BACKUP_COUNT = 5

class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour la console"""
    
    # Codes couleur ANSI
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Vert
        'WARNING': '\033[33m',  # Jaune
        'ERROR': '\033[31m',    # Rouge
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Application de la couleur
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

def setup_logger(log_level=None, log_to_console=True, log_to_file=True):
    """
    Configure le système de logging principal
    
    Args:
        log_level: Niveau de log (défaut: INFO)
        log_to_console (bool): Log vers la console
        log_to_file (bool): Log vers fichier
    """
    if log_level is None:
        log_level = LOG_LEVEL
    
    # Création du répertoire de logs
    Path(LOG_DIR).mkdir(exist_ok=True)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Suppression des handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler console
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Formatter avec couleurs si terminal supporte
        if sys.stdout.isatty() and not os.getenv('NO_COLOR'):
            console_formatter = ColoredFormatter(LOG_FORMAT, LOG_DATE_FORMAT)
        else:
            console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Handler fichier principal
    if log_to_file:
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, LOG_FILE),
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Handler fichier erreurs uniquement
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, ERROR_LOG_FILE),
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

def get_logger(name):
    """
    Retourne un logger configuré
    
    Args:
        name (str): Nom du logger (généralement __name__)
        
    Returns:
        logging.Logger: Logger configuré
    """
    return logging.getLogger(name)

class ModuleLogger:
    """Logger spécialisé pour les modules d'exploitation"""
    
    def __init__(self, module_name):
        self.module_name = module_name
        self.logger = get_logger(f"seullipeo.modules.{module_name}")
        self.start_time = datetime.now()
        
        # Log du démarrage du module
        self.logger.info(f"Module {module_name} initialisé")
    
    def scan_start(self):
        """Log du début de scan"""
        self.logger.info(f"Début du scan - Module {self.module_name}")
    
    def scan_end(self, vulnerabilities_count):
        """Log de fin de scan"""
        self.logger.info(f"Fin du scan - Module {self.module_name} - {vulnerabilities_count} vulnérabilités trouvées")
    
    def exploit_start(self, vulnerability):
        """Log du début d'exploitation"""
        vuln_desc = vulnerability.get('description', 'N/A')
        self.logger.info(f"Début exploitation - {vuln_desc}")
    
    def exploit_success(self, vulnerability, result):
        """Log d'exploitation réussie"""
        vuln_desc = vulnerability.get('description', 'N/A')
        self.logger.info(f"Exploitation réussie - {vuln_desc}")
    
    def exploit_failure(self, vulnerability, error):
        """Log d'exploitation échouée"""
        vuln_desc = vulnerability.get('description', 'N/A')
        self.logger.error(f"Exploitation échouée - {vuln_desc} - Erreur: {error}")
    
    def vulnerability_found(self, vulnerability):
        """Log d'une vulnérabilité trouvée"""
        vuln_desc = vulnerability.get('description', 'N/A')
        risk = vulnerability.get('risk', 'Unknown')
        self.logger.info(f"Vulnérabilité détectée [{risk}] - {vuln_desc}")
    
    def debug(self, message):
        """Log de debug"""
        self.logger.debug(f"[{self.module_name}] {message}")
    
    def info(self, message):
        """Log d'information"""
        self.logger.info(f"[{self.module_name}] {message}")
    
    def warning(self, message):
        """Log d'avertissement"""
        self.logger.warning(f"[{self.module_name}] {message}")
    
    def error(self, message):
        """Log d'erreur"""
        self.logger.error(f"[{self.module_name}] {message}")

class SessionLogger:
    """Logger pour une session d'utilisation"""
    
    def __init__(self, session_id=None):
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.session_id = session_id
        self.logger = get_logger(f"seullipeo.session.{session_id}")
        self.start_time = datetime.now()
        
        # Fichier de log spécifique à la session
        self.session_log_file = os.path.join(LOG_DIR, f"session_{session_id}.log")
        
        # Handler pour le fichier de session
        session_handler = logging.FileHandler(self.session_log_file, encoding='utf-8')
        session_handler.setLevel(logging.INFO)
        session_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
        session_handler.setFormatter(session_formatter)
        self.logger.addHandler(session_handler)
        
        # Log du début de session
        self.logger.info(f"Début de session: {session_id}")
    
    def command_executed(self, command, success=True):
        """Log d'une commande exécutée"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"COMMAND [{status}]: {command}")
    
    def module_loaded(self, module_name):
        """Log du chargement d'un module"""
        self.logger.info(f"MODULE LOADED: {module_name}")
    
    def vulnerability_exploited(self, module_name, vulnerability, success=True):
        """Log d'exploitation de vulnérabilité"""
        status = "SUCCESS" if success else "FAILED"
        vuln_desc = vulnerability.get('description', 'N/A')
        self.logger.info(f"EXPLOIT [{status}] {module_name}: {vuln_desc}")
    
    def session_end(self):
        """Log de fin de session"""
        duration = datetime.now() - self.start_time
        self.logger.info(f"Fin de session: {self.session_id} - Durée: {duration}")
    
    def get_session_log_path(self):
        """Retourne le chemin du fichier de log de session"""
        return self.session_log_file

def log_system_info():
    """Log des informations système au démarrage"""
    logger = get_logger("seullipeo.system")
    
    try:
        import platform
        from utils.system import get_current_user, is_root
        
        # Informations système
        logger.info(f"Système: {platform.system()} {platform.release()}")
        logger.info(f"Architecture: {platform.machine()}")
        logger.info(f"Python: {platform.python_version()}")
        
        # Informations utilisateur
        user_info = get_current_user()
        logger.info(f"Utilisateur: {user_info['username']} (UID: {user_info['uid']})")
        logger.info(f"Root: {'Oui' if is_root() else 'Non'}")
        
        # Répertoire de travail
        logger.info(f"Répertoire: {os.getcwd()}")
        
    except Exception as e:
        logger.error(f"Erreur lors du log des infos système: {e}")

def log_module_results(module_name, scan_results, exploit_results=None):
    """
    Log des résultats d'un module
    
    Args:
        module_name (str): Nom du module
        scan_results (list): Résultats du scan
        exploit_results (list): Résultats d'exploitation (optionnel)
    """
    logger = get_logger(f"seullipeo.results.{module_name}")
    
    # Résultats de scan
    logger.info(f"=== RÉSULTATS SCAN - {module_name.upper()} ===")
    logger.info(f"Vulnérabilités trouvées: {len(scan_results)}")
    
    for i, vuln in enumerate(scan_results, 1):
        risk = vuln.get('risk', 'Unknown')
        desc = vuln.get('description', 'N/A')
        path = vuln.get('path', 'N/A')
        logger.info(f"  {i:2d}. [{risk}] {desc} - {path}")
    
    # Résultats d'exploitation
    if exploit_results:
        logger.info(f"=== RÉSULTATS EXPLOITATION - {module_name.upper()} ===")
        success_count = sum(1 for r in exploit_results if r.get('success', False))
        logger.info(f"Exploits réussis: {success_count}/{len(exploit_results)}")
        
        for i, result in enumerate(exploit_results, 1):
            success = result.get('success', False)
            desc = result.get('description', 'N/A')
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"  {i:2d}. [{status}] {desc}")
            
            if not success and result.get('error'):
                logger.info(f"      Erreur: {result['error']}")

def setup_debug_logging():
    """Active le logging de debug"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Mise à jour des handlers existants
    for handler in root_logger.handlers:
        handler.setLevel(logging.DEBUG)

def disable_logging():
    """Désactive complètement le logging"""
    logging.disable(logging.CRITICAL)

def enable_logging():
    """Réactive le logging"""
    logging.disable(logging.NOTSET)

def get_log_stats():
    """
    Retourne des statistiques sur les logs
    
    Returns:
        dict: Statistiques des logs
    """
    stats = {
        'log_directory': LOG_DIR,
        'files': [],
        'total_size': 0
    }
    
    try:
        if os.path.exists(LOG_DIR):
            for filename in os.listdir(LOG_DIR):
                file_path = os.path.join(LOG_DIR, filename)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    stats['files'].append({
                        'name': filename,
                        'size': file_size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                    })
                    stats['total_size'] += file_size
    
    except Exception as e:
        logger = get_logger("seullipeo.logger")
        logger.error(f"Erreur récupération stats logs: {e}")
    
    return stats

def cleanup_old_logs(days=30):
    """
    Supprime les anciens fichiers de log
    
    Args:
        days (int): Nombre de jours à conserver
    """
    try:
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        if os.path.exists(LOG_DIR):
            for filename in os.listdir(LOG_DIR):
                file_path = os.path.join(LOG_DIR, filename)
                
                if os.path.isfile(file_path) and filename.endswith('.log'):
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
        
        logger = get_logger("seullipeo.logger")
        logger.info(f"Nettoyage logs: {deleted_count} fichiers supprimés")
        
    except Exception as e:
        logger = get_logger("seullipeo.logger")
        logger.error(f"Erreur nettoyage logs: {e}")

# Configuration par défaut au chargement du module
if not logging.getLogger().handlers:
    setup_logger()