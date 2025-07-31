"""
Module pour la gestion des couleurs dans le terminal
"""

import os
import sys


class Colors:
    """Codes ANSI pour les couleurs du terminal"""
    
    # Détection du support des couleurs
    SUPPORTS_COLOR = (
        sys.stdout.isatty() and
        os.environ.get('TERM') != 'dumb' and
        os.name != 'nt'  # Windows nécessite un traitement spécial
    )
    
    # Couleurs de base
    BLACK = '\033[30m' if SUPPORTS_COLOR else ''
    RED = '\033[31m' if SUPPORTS_COLOR else ''
    GREEN = '\033[32m' if SUPPORTS_COLOR else ''
    YELLOW = '\033[33m' if SUPPORTS_COLOR else ''
    BLUE = '\033[34m' if SUPPORTS_COLOR else ''
    MAGENTA = '\033[35m' if SUPPORTS_COLOR else ''
    CYAN = '\033[36m' if SUPPORTS_COLOR else ''
    WHITE = '\033[37m' if SUPPORTS_COLOR else ''
    
    # Couleurs brillantes
    BRIGHT_BLACK = '\033[90m' if SUPPORTS_COLOR else ''
    BRIGHT_RED = '\033[91m' if SUPPORTS_COLOR else ''
    BRIGHT_GREEN = '\033[92m' if SUPPORTS_COLOR else ''
    BRIGHT_YELLOW = '\033[93m' if SUPPORTS_COLOR else ''
    BRIGHT_BLUE = '\033[94m' if SUPPORTS_COLOR else ''
    BRIGHT_MAGENTA = '\033[95m' if SUPPORTS_COLOR else ''
    BRIGHT_CYAN = '\033[96m' if SUPPORTS_COLOR else ''
    BRIGHT_WHITE = '\033[97m' if SUPPORTS_COLOR else ''
    
    # Styles
    BOLD = '\033[1m' if SUPPORTS_COLOR else ''
    DIM = '\033[2m' if SUPPORTS_COLOR else ''
    ITALIC = '\033[3m' if SUPPORTS_COLOR else ''
    UNDERLINE = '\033[4m' if SUPPORTS_COLOR else ''
    BLINK = '\033[5m' if SUPPORTS_COLOR else ''
    REVERSE = '\033[7m' if SUPPORTS_COLOR else ''
    HIDDEN = '\033[8m' if SUPPORTS_COLOR else ''
    STRIKETHROUGH = '\033[9m' if SUPPORTS_COLOR else ''
    
    # Reset
    RESET = '\033[0m' if SUPPORTS_COLOR else ''
    
    @classmethod
    def disable(cls):
        """Désactiver les couleurs"""
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith('_'):
                setattr(cls, attr, '')
    
    @classmethod
    def enable(cls):
        """Réactiver les couleurs"""
        cls.__init__()
    
    @staticmethod
    def colorize(text, color):
        """Coloriser un texte"""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text):
        """Texte de succès (vert)"""
        return Colors.colorize(text, Colors.GREEN)
    
    @staticmethod
    def error(text):
        """Texte d'erreur (rouge)"""
        return Colors.colorize(text, Colors.RED)
    
    @staticmethod
    def warning(text):
        """Texte d'avertissement (jaune)"""
        return Colors.colorize(text, Colors.YELLOW)
    
    @staticmethod
    def info(text):
        """Texte d'information (cyan)"""
        return Colors.colorize(text, Colors.CYAN)
    
    @staticmethod
    def highlight(text):
        """Texte en surbrillance (magenta)"""
        return Colors.colorize(text, Colors.BRIGHT_MAGENTA)


def print_banner():
    """Afficher la bannière Gieokja"""
    banner = f"""
{Colors.CYAN}╔════════════════════════════════════════════════════════╗
║                                                        ║
║  {Colors.BRIGHT_CYAN}🧠  Gieokja (기억자) - The Rememberer  🧠{Colors.CYAN}          ║
║                                                        ║
║  {Colors.WHITE}Votre compagnon de documentation CTF automatique{Colors.CYAN}     ║
║  {Colors.WHITE}Capture • Organise • Documente{Colors.CYAN}                       ║
║                                                        ║
╚════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_colored_table(headers, rows, colors=None):
    """Afficher un tableau coloré"""
    if not colors:
        colors = [Colors.WHITE] * len(headers)
    
    # Calculer les largeurs de colonnes
    col_widths = []
    for i, header in enumerate(headers):
        width = len(header)
        for row in rows:
            if i < len(row):
                width = max(width, len(str(row[i])))
        col_widths.append(width + 2)
    
    # Afficher l'en-tête
    header_line = ""
    for i, header in enumerate(headers):
        header_line += f"{colors[i]}{header.center(col_widths[i])}{Colors.RESET}"
    print(header_line)
    
    # Ligne de séparation
    sep_line = ""
    for width in col_widths:
        sep_line += "-" * width
    print(Colors.DIM + sep_line + Colors.RESET)
    
    # Afficher les lignes
    for row in rows:
        row_line = ""
        for i, cell in enumerate(row):
            if i < len(colors):
                row_line += f"{colors[i]}{str(cell).ljust(col_widths[i])}{Colors.RESET}"
            else:
                row_line += str(cell).ljust(col_widths[i])
        print(row_line)


# Support Windows (colorama)
if os.name == 'nt':
    try:
        import colorama
        colorama.init(autoreset=True)
        Colors.SUPPORTS_COLOR = True
    except ImportError:
        Colors.disable()