#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package utils pour Seullipeo
Utilitaires pour affichage, système et logging
"""

__version__ = "1.0.0"

# Import des modules principaux
from .display import (
    print_colored, show_banner, print_status, print_table,
    print_separator, print_box, clear_screen, show_help_menu
)

from .system import (
    run_command, is_root, get_current_user, is_writable,
    get_file_permissions, get_system_info, check_command_exists
)

from .logger import (
    setup_logger, get_logger, ModuleLogger, SessionLogger,
    log_system_info, setup_debug_logging
)

__all__ = [
    # Display
    'print_colored',
    'show_banner', 
    'print_status',
    'print_table',
    'print_separator',
    'print_box',
    'clear_screen',
    'show_help_menu',
    
    # System
    'run_command',
    'is_root',
    'get_current_user',
    'is_writable',
    'get_file_permissions',
    'get_system_info',
    'check_command_exists',
    
    # Logger
    'setup_logger',
    'get_logger',
    'ModuleLogger',
    'SessionLogger',
    'log_system_info',
    'setup_debug_logging'
]