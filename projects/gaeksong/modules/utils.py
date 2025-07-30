#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module utilitaire
Fonctions de support pour logging, validation et affichage
"""

import re
import os
import logging
from datetime import datetime

# Configuration du logging
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_FILE = 'gaeksong.log'

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('gaeksong')

def log(message, level="info"):
    """
    Fonction de logging avec différents niveaux
    
    Args:
        message (str): Message à logger
        level (str): Niveau de log (info, warning, error, debug)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level.lower() == "info":
        logger.info(message)
    elif level.lower() == "warning":
        logger.warning(message)
    elif level.lower() == "error":
        logger.error(message)
    elif level.lower() == "debug":
        logger.debug(message)
    else:
        logger.info(message)

def validate_domain(domain):
    """
    Valide le format d'un nom de domaine
    
    Args:
        domain (str): Domaine à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    if not domain or len(domain) > 253:
        return False
    
    # Regex pour valider un domaine
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    return bool(domain_pattern.match(domain))

def validate_ip(ip):
    """
    Valide le format d'une adresse IP
    
    Args:
        ip (str): Adresse IP à valider
        
    Returns:
        bool: True si valide, False sinon
    """
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False

def load_wordlist(wordlist_path):
    """
    Charge une wordlist depuis un fichier
    
    Args:
        wordlist_path (str): Chemin vers le fichier wordlist
        
    Returns:
        list: Liste des mots ou None en cas d'erreur
    """
    try:
        if not os.path.exists(wordlist_path):
            log(f"Fichier wordlist introuvable: {wordlist_path}", "error")
            return None
        
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            wordlist = [line.strip() for line in f if line.strip()]
        
        log(f"Wordlist chargée: {len(wordlist)} entrées depuis {wordlist_path}", "info")
        return wordlist
        
    except Exception as e:
        log(f"Erreur lors du chargement de la wordlist {wordlist_path}: {str(e)}", "error")
        return None

def print_colored(message, color="white"):
    """
    Affiche un message coloré dans le terminal
    
    Args:
        message (str): Message à afficher
        color (str): Couleur (red, green, blue, yellow, white)
    """
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'yellow': '\033[93m',
        'white': '\033[0m',
        'cyan': '\033[96m',
        'magenta': '\033[95m'
    }
    
    reset = '\033[0m'
    color_code = colors.get(color.lower(), colors['white'])
    
    print(f"{color_code}{message}{reset}")

def create_banner():
    """
    Affiche la bannière de l'outil
    """
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗  █████╗ ███████╗██╗  ██╗███████╗ ██████╗ ███╗   ██╗ ║
    ║  ██╔════╝ ██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔═══██╗████╗  ██║ ║
    ║  ██║  ███╗███████║█████╗  █████╔╝ ███████╗██║   ██║██╔██╗ ██║ ║
    ║  ██║   ██║██╔══██║██╔══╝  ██╔═██╗ ╚════██║██║   ██║██║╚██╗██║ ║
    ║  ╚██████╔╝██║  ██║███████╗██║  ██╗███████║╚██████╔╝██║ ╚████║ ║
    ║   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ ║
    ║                                                               ║
    ║           Outil de Reconnaissance Active et Passive          ║
    ║                     Version 1.0 - 2025                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, "cyan")

def format_file_size(size_bytes):
    """
    Formate une taille de fichier en format lisible
    
    Args:
        size_bytes (int): Taille en bytes
        
    Returns:
        str: Taille formatée
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def sanitize_filename(filename):
    """
    Nettoie un nom de fichier en supprimant les caractères invalides
    
    Args:
        filename (str): Nom de fichier à nettoyer
        
    Returns:
        str: Nom de fichier nettoyé
    """
    # Suppression des caractères interdits
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitation de la longueur
    if len(filename) > 250:
        filename = filename[:250]
    
    return filename

def progress_bar(current, total, bar_length=50):
    """
    Affiche une barre de progression
    
    Args:
        current (int): Valeur actuelle
        total (int): Valeur totale
        bar_length (int): Longueur de la barre
    """
    if total == 0:
        percent = 100
    else:
        percent = (current / total) * 100
    
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    print(f'\r|{bar}| {percent:.1f}% ({current}/{total})', end='', flush=True)
    
    if current == total:
        print()  # Nouvelle ligne à la fin

def get_timestamp():
    """
    Retourne un timestamp formaté
    
    Returns:
        str: Timestamp au format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def ensure_directory(directory_path):
    """
    S'assure qu'un répertoire existe, le crée sinon
    
    Args:
        directory_path (str): Chemin du répertoire
        
    Returns:
        bool: True si le répertoire existe ou a été créé, False sinon
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        log(f"Erreur lors de la création du répertoire {directory_path}: {str(e)}", "error")
        return False

def is_port_valid(port):
    """
    Vérifie si un numéro de port est valide
    
    Args:
        port (int): Numéro de port à vérifier
        
    Returns:
        bool: True si valide, False sinon
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False

def parse_port_range(port_string):
    """
    Parse une chaîne de ports (ex: "22,80,443,8000-8100")
    
    Args:
        port_string (str): Chaîne de ports à parser
        
    Returns:
        list: Liste des ports ou None en cas d'erreur
    """
    try:
        ports = []
        parts = port_string.split(',')
        
        for part in parts:
            part = part.strip()
            
            if '-' in part:
                # Plage de ports
                start, end = part.split('-')
                start, end = int(start.strip()), int(end.strip())
                
                if start > end:
                    start, end = end, start
                
                for port in range(start, end + 1):
                    if is_port_valid(port):
                        ports.append(port)
            else:
                # Port simple
                port = int(part)
                if is_port_valid(port):
                    ports.append(port)
        
        return sorted(list(set(ports)))  # Suppression des doublons et tri
        
    except Exception as e:
        log(f"Erreur lors du parsing des ports '{port_string}': {str(e)}", "error")
        return None