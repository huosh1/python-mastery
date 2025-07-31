"""
Module de logging pour Gieokja
"""

import logging
import os
from datetime import datetime
from pathlib import Path


# Configuration globale du logger
_logger = None
_log_file = None


def setup_logger(log_level=logging.INFO, log_file="logs/gieokja.log"):
    """Configurer le logger principal"""
    global _logger, _log_file
    
    if _logger:
        return _logger
    
    # Créer le répertoire de logs
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    _log_file = log_file
    
    # Créer le logger
    _logger = logging.getLogger('gieokja')
    _logger.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    # Handler pour console (seulement pour les erreurs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    
    # Vérifier si on doit afficher les erreurs dans la console
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        if not config.getboolean('general', 'console_log_errors', fallback=True):
            console_handler.setLevel(logging.CRITICAL + 1)  # Désactiver complètement
    except:
        pass
    
    _logger.addHandler(console_handler)
    
    _logger.info("=== Gieokja démarré ===")
    
    return _logger


def get_logger():
    """Obtenir le logger existant"""
    global _logger
    
    if not _logger:
        _logger = setup_logger()
    
    return _logger


def log_command(command, output=None, error=None):
    """Logger une commande exécutée"""
    logger = get_logger()
    
    log_entry = f"COMMAND: {command}"
    if output:
        log_entry += f"\nOUTPUT: {output[:500]}..."  # Limiter la taille
    if error:
        log_entry += f"\nERROR: {error}"
    
    logger.info(log_entry)


def log_event(event_type, description, details=None):
    """Logger un événement"""
    logger = get_logger()
    
    log_entry = f"EVENT [{event_type}]: {description}"
    if details:
        log_entry += f"\nDETAILS: {details}"
    
    logger.info(log_entry)


def log_error(error_msg, exception=None):
    """Logger une erreur"""
    logger = get_logger()
    
    if exception:
        logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
    else:
        logger.error(error_msg)


def get_log_file_path():
    """Obtenir le chemin du fichier de log"""
    global _log_file
    return _log_file


def rotate_logs(max_size_mb=10, max_files=5):
    """Rotation des logs si nécessaire"""
    global _log_file
    
    if not _log_file:
        return
    
    log_path = Path(_log_file)
    
    # Vérifier la taille du fichier
    if log_path.exists():
        size_mb = log_path.stat().st_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            # Renommer les anciens logs
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = log_path.stem + f"_{timestamp}" + log_path.suffix
            new_path = log_path.parent / new_name
            
            log_path.rename(new_path)
            
            # Nettoyer les vieux logs
            log_files = sorted(log_path.parent.glob(f"{log_path.stem}_*{log_path.suffix}"))
            if len(log_files) > max_files:
                for old_file in log_files[:-max_files]:
                    old_file.unlink()
            
            # Recréer le logger
            global _logger
            _logger = None
            setup_logger()


class LogContext:
    """Contexte de logging pour des opérations spécifiques"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = get_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Début de l'opération: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        
        if exc_type:
            self.logger.error(
                f"Erreur dans l'opération {self.operation_name}: {exc_val}",
                exc_info=True
            )
        else:
            self.logger.info(
                f"Fin de l'opération: {self.operation_name} (durée: {duration})"
            )
        
        return False  # Propager l'exception


# Fonction utilitaire pour debug
def debug_log(message, data=None):
    """Logger un message de debug avec données optionnelles"""
    logger = get_logger()
    
    if logger.isEnabledFor(logging.DEBUG):
        if data:
            import json
            try:
                data_str = json.dumps(data, indent=2, default=str)
                logger.debug(f"{message}\n{data_str}")
            except:
                logger.debug(f"{message}\n{repr(data)}")
        else:
            logger.debug(message)