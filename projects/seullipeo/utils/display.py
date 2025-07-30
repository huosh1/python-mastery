#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires d'affichage pour Seullipeo
Bannières, couleurs, formatage
"""

import os
import sys
from datetime import datetime

# Codes couleur ANSI
class Colors:
    # Couleurs de base
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Couleurs vives
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'
    END = '\033[0m'

def supports_color():
    """
    Vérifie si le terminal supporte les couleurs
    
    Returns:
        bool: True si les couleurs sont supportées
    """
    # Vérification des variables d'environnement
    if os.getenv('NO_COLOR'):
        return False
    
    if os.getenv('FORCE_COLOR'):
        return True
    
    # Vérification si on est dans un terminal
    if not sys.stdout.isatty():
        return False
    
    # Vérification du type de terminal
    term = os.getenv('TERM', '').lower()
    if 'color' in term or 'xterm' in term or 'screen' in term:
        return True
    
    return False

def print_colored(text, color="white", style=None, return_string=False):
    """
    Affiche du texte coloré
    
    Args:
        text (str): Texte à afficher
        color (str): Couleur du texte
        style (str): Style du texte (bold, underline, etc.)
        return_string (bool): Si True, retourne la string au lieu de l'afficher
    
    Returns:
        str: String formatée si return_string=True
    """
    if not supports_color():
        if return_string:
            return text
        print(text)
        return
    
    # Mapping des couleurs
    color_map = {
        'black': Colors.BLACK,
        'red': Colors.RED,
        'green': Colors.GREEN,
        'yellow': Colors.YELLOW,
        'blue': Colors.BLUE,
        'magenta': Colors.MAGENTA,
        'cyan': Colors.CYAN,
        'white': Colors.WHITE,
        'bright_red': Colors.BRIGHT_RED,
        'bright_green': Colors.BRIGHT_GREEN,
        'bright_yellow': Colors.BRIGHT_YELLOW,
        'bright_blue': Colors.BRIGHT_BLUE,
        'bright_magenta': Colors.BRIGHT_MAGENTA,
        'bright_cyan': Colors.BRIGHT_CYAN,
        'bright_white': Colors.BRIGHT_WHITE
    }
    
    # Mapping des styles
    style_map = {
        'bold': Colors.BOLD,
        'dim': Colors.DIM,
        'underline': Colors.UNDERLINE,
        'blink': Colors.BLINK,
        'reverse': Colors.REVERSE
    }
    
    # Construction de la string formatée
    color_code = color_map.get(color.lower(), Colors.WHITE)
    style_code = style_map.get(style.lower(), '') if style else ''
    
    formatted_text = f"{style_code}{color_code}{text}{Colors.RESET}"
    
    if return_string:
        return formatted_text
    
    print(formatted_text)

def show_banner():
    """Affiche la bannière principale de Seullipeo"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗███████╗██╗   ██╗██╗     ██╗     ██╗██████╗ ███████╗ ██████╗     ║
║     ██╔════╝██╔════╝██║   ██║██║     ██║     ██║██╔══██╗██╔════╝██╔═══██╗    ║
║     ███████╗█████╗  ██║   ██║██║     ██║     ██║██████╔╝█████╗  ██║   ██║    ║
║     ╚════██║██╔══╝  ██║   ██║██║     ██║     ██║██╔═══╝ ██╔══╝  ██║   ██║    ║
║     ███████║███████╗╚██████╔╝███████╗███████╗██║██║     ███████╗╚██████╔╝    ║
║     ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝     ╚══════╝ ╚═════╝     ║
║                                                                              ║
║                           슬리퍼 (Sleeper)                                    ║
║                    Linux Privilege Escalation Framework                      ║
║                                                                              ║
║                              Version 1.0.0                                  ║
║                           Seullipeo Team - 2025                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    
    print_colored(banner, "cyan")
    print_colored("   [!] À des fins éducatives et de test autorisé uniquement", "yellow")
    print_colored("   [!] L'auteur décline toute responsabilité en cas d'usage malveillant\n", "yellow")

def show_ascii_art():
    """Affiche l'art ASCII alternatif"""
    art = """
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    █ ███████ ███████ ██   ██ ██      ██      ██ ██████  ███████  ██████      █
    █ ██      ██      ██   ██ ██      ██      ██ ██   ██ ██      ██    ██     █
    █ ███████ █████   ██   ██ ██      ██      ██ ██████  █████   ██    ██     █
    █      ██ ██      ██   ██ ██      ██      ██ ██      ██      ██    ██     █
    █ ███████ ███████  █████  ███████ ███████ ██ ██      ███████  ██████      █
    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
    """
    print_colored(art, "red")

def show_module_banner(module_name):
    """
    Affiche une bannière pour un module spécifique
    
    Args:
        module_name (str): Nom du module
    """
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              MODULE: {module_name.upper():<20}                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, "blue")

def create_table(headers, rows, title=None):
    """
    Crée un tableau formaté
    
    Args:
        headers (list): En-têtes du tableau
        rows (list): Lignes de données
        title (str): Titre optionnel du tableau
    
    Returns:
        str: Tableau formaté
    """
    if not headers or not rows:
        return ""
    
    # Calcul des largeurs des colonnes
    col_widths = [len(str(header)) for header in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Construction du tableau
    table_lines = []
    
    # Titre optionnel
    if title:
        total_width = sum(col_widths) + len(col_widths) * 3 + 1
        title_line = f"║ {title:<{total_width-4}} ║"
        table_lines.append("╔" + "═" * (total_width-2) + "╗")
        table_lines.append(title_line)
        table_lines.append("╠" + "═" * (total_width-2) + "╣")
    
    # En-têtes
    header_line = "║"
    separator_line = "╠"
    
    for i, header in enumerate(headers):
        header_line += f" {header:<{col_widths[i]}} ║"
        separator_line += "═" * (col_widths[i] + 2) + "╬" if i < len(headers)-1 else "═" * (col_widths[i] + 2) + "╣"
    
    if not title:
        table_lines.append("╔" + "═" * (len(header_line)-2) + "╗")
    
    table_lines.append(header_line)
    table_lines.append(separator_line)
    
    # Lignes de données
    for row in rows:
        row_line = "║"
        for i, cell in enumerate(row):
            if i < len(col_widths):
                row_line += f" {str(cell):<{col_widths[i]}} ║"
        table_lines.append(row_line)
    
    # Ligne de fermeture
    table_lines.append("╚" + "═" * (len(header_line)-2) + "╝")
    
    return "\n".join(table_lines)

def print_table(headers, rows, title=None):
    """
    Affiche un tableau formaté
    
    Args:
        headers (list): En-têtes du tableau
        rows (list): Lignes de données
        title (str): Titre optionnel du tableau
    """
    table = create_table(headers, rows, title)
    print_colored(table, "white")

def print_status(message, status="info"):
    """
    Affiche un message de statut formaté
    
    Args:
        message (str): Message à afficher
        status (str): Type de statut (info, success, warning, error)
    """
    status_symbols = {
        'info': '[*]',
        'success': '[+]',
        'warning': '[!]',
        'error': '[-]',
        'question': '[?]',
        'debug': '[D]'
    }
    
    status_colors = {
        'info': 'blue',
        'success': 'green',
        'warning': 'yellow',
        'error': 'red',
        'question': 'cyan',
        'debug': 'magenta'
    }
    
    symbol = status_symbols.get(status, '[*]')
    color = status_colors.get(status, 'white')
    
    print_colored(f"{symbol} {message}", color)

def print_separator(char="=", length=80, color="cyan"):
    """
    Affiche un séparateur
    
    Args:
        char (str): Caractère à utiliser
        length (int): Longueur du séparateur
        color (str): Couleur du séparateur
    """
    print_colored(char * length, color)

def print_box(text, color="white", padding=2):
    """
    Affiche du texte dans une boîte
    
    Args:
        text (str): Texte à afficher
        color (str): Couleur de la boîte
        padding (int): Padding interne
    """
    lines = text.split('\n')
    max_length = max(len(line) for line in lines)
    
    box_width = max_length + (padding * 2)
    
    # Ligne du haut
    print_colored("╔" + "═" * box_width + "╗", color)
    
    # Lignes vides de padding
    for _ in range(padding // 2):
        print_colored("║" + " " * box_width + "║", color)
    
    # Contenu
    for line in lines:
        padded_line = line.center(box_width)
        print_colored(f"║{padded_line}║", color)
    
    # Lignes vides de padding
    for _ in range(padding // 2):
        print_colored("║" + " " * box_width + "║", color)
    
    # Ligne du bas
    print_colored("╚" + "═" * box_width + "╝", color)

def print_progress_bar(current, total, bar_length=50, prefix="Progress"):
    """
    Affiche une barre de progression
    
    Args:
        current (int): Valeur actuelle
        total (int): Valeur totale
        bar_length (int): Longueur de la barre
        prefix (str): Préfixe à afficher
    """
    if total == 0:
        percent = 100
    else:
        percent = (current / total) * 100
    
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    progress_text = f'{prefix}: |{bar}| {percent:.1f}% ({current}/{total})'
    print_colored(f'\r{progress_text}', 'cyan', return_string=False)
    
    if current == total:
        print()  # Nouvelle ligne à la fin

def clear_screen():
    """Nettoie l'écran du terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_vulnerability_summary(vulnerabilities):
    """
    Affiche un résumé des vulnérabilités trouvées
    
    Args:
        vulnerabilities (list): Liste des vulnérabilités
    """
    if not vulnerabilities:
        print_status("Aucune vulnérabilité trouvée", "info")
        return
    
    # Comptage par niveau de risque
    risk_counts = {}
    for vuln in vulnerabilities:
        risk = vuln.get('risk', 'Unknown')
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print_separator("=", 60, "cyan")
    print_colored("RÉSUMÉ DES VULNÉRABILITÉS", "cyan", "bold")
    print_separator("=", 60, "cyan")
    
    # Affichage des compteurs
    risk_colors = {
        'Critical': 'bright_red',
        'High': 'red',
        'Medium': 'yellow',
        'Low': 'green',
        'Unknown': 'white'
    }
    
    total = len(vulnerabilities)
    print_status(f"Total des vulnérabilités: {total}", "info")
    
    for risk, count in sorted(risk_counts.items(), key=lambda x: ['Critical', 'High', 'Medium', 'Low', 'Unknown'].index(x[0]) if x[0] in ['Critical', 'High', 'Medium', 'Low', 'Unknown'] else 999):
        color = risk_colors.get(risk, 'white')
        print_colored(f"  {risk}: {count}", color)
    
    print()

def print_exploit_results(results):
    """
    Affiche les résultats d'exploitation
    
    Args:
        results (list): Liste des résultats d'exploitation
    """
    if not results:
        print_status("Aucun résultat d'exploitation", "info")
        return
    
    print_separator("=", 60, "green")
    print_colored("RÉSULTATS D'EXPLOITATION", "green", "bold")
    print_separator("=", 60, "green")
    
    success_count = sum(1 for r in results if r.get('success', False))
    failure_count = len(results) - success_count
    
    print_status(f"Exploits réussis: {success_count}", "success")
    print_status(f"Exploits échoués: {failure_count}", "error")
    print()
    
    # Détails des résultats
    for i, result in enumerate(results, 1):
        if result.get('success', False):
            print_colored(f"{i:2d}. ✓ {result.get('description', 'N/A')}", "green")
            if result.get('details'):
                print_colored(f"      {result['details']}", "cyan")
        else:
            print_colored(f"{i:2d}. ✗ {result.get('description', 'N/A')}", "red")
            if result.get('error'):
                print_colored(f"      Erreur: {result['error']}", "yellow")
    
    print()

def show_help_menu():
    """Affiche le menu d'aide principal"""
    help_text = """
UTILISATION DE SEULLIPEO

Mode CLI:
  python3 main.py --scan --cron --suid --output results.txt
  python3 main.py --exploit --passwd --json results.json
  python3 main.py --aggressive --all-modules

Mode Shell interactif:
  python3 main.py --shell

Modules disponibles:
  --cron          Exploitation des tâches cron vulnérables
  --suid          Détection des binaires SUID exploitables
  --passwd        Exploitation /etc/passwd modifiable

Options:
  --scan          Scan uniquement (pas d'exploitation)
  --exploit       Exploitation directe
  --aggressive    Scan + exploit automatique
  --output FILE   Sauvegarde en format texte
  --json FILE     Sauvegarde en format JSON
    """
    
    print_box(help_text, "blue", 2)

def format_file_size(size_bytes):
    """
    Formate une taille de fichier
    
    Args:
        size_bytes (int): Taille en bytes
        
    Returns:
        str: Taille formatée
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def format_timestamp(timestamp=None):
    """
    Formate un timestamp
    
    Args:
        timestamp: Timestamp à formater (défaut: maintenant)
        
    Returns:
        str: Timestamp formaté
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def print_module_info(module_info):
    """
    Affiche les informations d'un module
    
    Args:
        module_info (dict): Informations du module
    """
    print_separator("-", 50, "blue")
    print_colored(f"MODULE: {module_info.get('name', 'N/A').upper()}", "blue", "bold")
    print_separator("-", 50, "blue")
    
    info_items = [
        ("Description", module_info.get('description', 'N/A')),
        ("Auteur", module_info.get('author', 'N/A')),
        ("Risque", module_info.get('risk', 'N/A')),
        ("Cibles", ', '.join(module_info.get('targets', ['N/A']))),
        ("Disponible", "✓" if module_info.get('available', True) else "✗")
    ]
    
    for label, value in info_items:
        print_colored(f"{label:<12}: {value}", "white")
    
    if module_info.get('options'):
        print_colored("\nOptions:", "yellow")
        for opt, desc in module_info['options'].items():
            print_colored(f"  {opt:<15}: {desc}", "white")
    
    print()