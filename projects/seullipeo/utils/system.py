#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilitaires système pour Seullipeo
Fonctions pour exécution de commandes, vérifications de permissions, etc.
"""

import os
import stat
import subprocess
import pwd
import grp
import platform
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)

def run_command(command, shell=False, timeout=30, cwd=None):
    """
    Exécute une commande système
    
    Args:
        command (str|list): Commande à exécuter
        shell (bool): Utiliser le shell
        timeout (int): Timeout en secondes
        cwd (str): Répertoire de travail
        
    Returns:
        dict: Résultat avec success, output, error, returncode
    """
    try:
        if isinstance(command, str) and not shell:
            command = command.split()
        
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip(),
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout pour la commande: {command}")
        return {
            'success': False,
            'output': '',
            'error': f'Timeout après {timeout} secondes',
            'returncode': -1
        }
    except Exception as e:
        logger.error(f"Erreur exécution commande {command}: {e}")
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'returncode': -1
        }

def is_root():
    """
    Vérifie si l'utilisateur courant est root
    
    Returns:
        bool: True si root
    """
    return os.geteuid() == 0

def get_current_user():
    """
    Retourne l'utilisateur courant
    
    Returns:
        dict: Informations sur l'utilisateur
    """
    try:
        uid = os.getuid()
        user_info = pwd.getpwuid(uid)
        
        return {
            'uid': uid,
            'username': user_info.pw_name,
            'home': user_info.pw_dir,
            'shell': user_info.pw_shell,
            'gid': user_info.pw_gid
        }
    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {e}")
        return {
            'uid': uid if 'uid' in locals() else -1,
            'username': 'unknown',
            'home': '/tmp',
            'shell': '/bin/sh',
            'gid': -1
        }

def get_user_groups(username=None):
    """
    Retourne les groupes d'un utilisateur
    
    Args:
        username (str): Nom d'utilisateur (défaut: utilisateur courant)
        
    Returns:
        list: Liste des groupes
    """
    try:
        if username is None:
            username = get_current_user()['username']
        
        # Récupération des groupes via getent ou /etc/group
        result = run_command(['groups', username])
        if result['success']:
            groups_line = result['output']
            # Format: "username : group1 group2 group3"
            if ':' in groups_line:
                groups_part = groups_line.split(':', 1)[1].strip()
                return groups_part.split() if groups_part else []
            else:
                # Parfois le format est juste "group1 group2 group3"
                return groups_line.split()[1:] if groups_line.split() else []
        
        # Méthode alternative
        user_info = pwd.getpwnam(username)
        primary_gid = user_info.pw_gid
        groups = [grp.getgrgid(primary_gid).gr_name]
        
        # Groupes secondaires
        for group in grp.getgrall():
            if username in group.gr_mem and group.gr_name not in groups:
                groups.append(group.gr_name)
        
        return groups
        
    except Exception as e:
        logger.error(f"Erreur récupération groupes pour {username}: {e}")
        return []

def is_writable(file_path):
    """
    Vérifie si un fichier/répertoire est modifiable
    
    Args:
        file_path (str): Chemin à vérifier
        
    Returns:
        bool: True si modifiable
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return False
        
        # Test d'écriture direct
        return os.access(file_path, os.W_OK)
        
    except Exception as e:
        logger.debug(f"Erreur vérification écriture {file_path}: {e}")
        return False

def is_readable(file_path):
    """
    Vérifie si un fichier est lisible
    
    Args:
        file_path (str): Chemin à vérifier
        
    Returns:
        bool: True si lisible
    """
    try:
        return os.access(file_path, os.R_OK)
    except Exception:
        return False

def is_executable(file_path):
    """
    Vérifie si un fichier est exécutable
    
    Args:
        file_path (str): Chemin à vérifier
        
    Returns:
        bool: True si exécutable
    """
    try:
        return os.access(file_path, os.X_OK)
    except Exception:
        return False

def get_file_permissions(file_path):
    """
    Retourne les permissions détaillées d'un fichier
    
    Args:
        file_path (str): Chemin du fichier
        
    Returns:
        dict: Informations sur les permissions
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        stat_info = path.stat()
        file_mode = stat_info.st_mode
        
        # Permissions octales
        perms_octal = oct(file_mode)[-3:]
        
        # Permissions symboliques
        perms_symbolic = stat.filemode(file_mode)
        
        # Type de fichier
        file_type = 'file'
        if stat.S_ISDIR(file_mode):
            file_type = 'directory'
        elif stat.S_ISLNK(file_mode):
            file_type = 'symlink'
        elif stat.S_ISBLK(file_mode):
            file_type = 'block_device'
        elif stat.S_ISCHR(file_mode):
            file_type = 'char_device'
        elif stat.S_ISFIFO(file_mode):
            file_type = 'fifo'
        elif stat.S_ISSOCK(file_mode):
            file_type = 'socket'
        
        # Propriétaire et groupe
        try:
            owner = pwd.getpwuid(stat_info.st_uid).pw_name
        except KeyError:
            owner = str(stat_info.st_uid)
        
        try:
            group = grp.getgrgid(stat_info.st_gid).gr_name
        except KeyError:
            group = str(stat_info.st_gid)
        
        # Bits spéciaux
        special_bits = {
            'suid': bool(file_mode & stat.S_ISUID),
            'sgid': bool(file_mode & stat.S_ISGID),
            'sticky': bool(file_mode & stat.S_ISVTX)
        }
        
        return {
            'path': str(path),
            'type': file_type,
            'mode': file_mode,
            'octal': perms_octal,
            'symbolic': perms_symbolic,
            'owner': owner,
            'group': group,
            'uid': stat_info.st_uid,
            'gid': stat_info.st_gid,
            'size': stat_info.st_size,
            'special_bits': special_bits,
            'readable': is_readable(file_path),
            'writable': is_writable(file_path),
            'executable': is_executable(file_path)
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse permissions {file_path}: {e}")
        return None

def find_files_by_permissions(search_paths, permission_mask, file_type='f'):
    """
    Trouve les fichiers avec des permissions spécifiques
    
    Args:
        search_paths (list): Chemins de recherche
        permission_mask (str): Masque de permissions (ex: '4000' pour SUID)
        file_type (str): Type de fichier ('f', 'd', 'l')
        
    Returns:
        list: Liste des fichiers trouvés
    """
    found_files = []
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
        
        try:
            # Utilisation de find si disponible
            cmd = [
                'find', search_path,
                '-type', file_type,
                '-perm', f'-{permission_mask}',
                '2>/dev/null'
            ]
            
            result = run_command(cmd, shell=True)
            
            if result['success']:
                for line in result['output'].split('\n'):
                    if line.strip():
                        found_files.append(line.strip())
            
        except Exception as e:
            logger.debug(f"Erreur find dans {search_path}: {e}")
            
            # Recherche manuelle en fallback
            try:
                for root, dirs, files in os.walk(search_path):
                    # Limitation de profondeur
                    if root.count(os.sep) - search_path.count(os.sep) > 3:
                        continue
                    
                    items = files if file_type == 'f' else dirs
                    
                    for item in items:
                        item_path = os.path.join(root, item)
                        
                        try:
                            file_stat = os.stat(item_path)
                            # Vérification du masque de permissions
                            if file_stat.st_mode & int(permission_mask, 8):
                                found_files.append(item_path)
                        except (OSError, ValueError):
                            continue
                            
            except (OSError, PermissionError):
                continue
    
    return found_files

def get_system_info():
    """
    Retourne les informations système
    
    Returns:
        dict: Informations système
    """
    try:
        # Informations de base
        uname_info = platform.uname()
        
        # Distribution Linux
        distro_info = {}
        if os.path.exists('/etc/os-release'):
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            distro_info[key] = value.strip('"')
            except Exception:
                pass
        
        # Version du kernel
        kernel_version = ''
        try:
            result = run_command(['uname', '-r'])
            if result['success']:
                kernel_version = result['output']
        except Exception:
            pass
        
        # Informations sur l'utilisateur
        user_info = get_current_user()
        user_groups = get_user_groups()
        
        return {
            'system': uname_info.system,
            'node': uname_info.node,
            'release': uname_info.release,
            'version': uname_info.version,
            'machine': uname_info.machine,
            'processor': uname_info.processor,
            'kernel_version': kernel_version,
            'distribution': distro_info,
            'user': user_info,
            'groups': user_groups,
            'is_root': is_root(),
            'python_version': platform.python_version()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération infos système: {e}")
        return {}

def check_command_exists(command):
    """
    Vérifie si une commande existe sur le système
    
    Args:
        command (str): Nom de la commande
        
    Returns:
        bool: True si la commande existe
    """
    try:
        result = run_command(['which', command])
        return result['success'] and result['output']
    except Exception:
        return False

def get_env_variable(var_name, default=None):
    """
    Récupère une variable d'environnement
    
    Args:
        var_name (str): Nom de la variable
        default: Valeur par défaut
        
    Returns:
        str: Valeur de la variable
    """
    return os.getenv(var_name, default)

def set_env_variable(var_name, value):
    """
    Définit une variable d'environnement
    
    Args:
        var_name (str): Nom de la variable
        value (str): Valeur à définir
    """
    os.environ[var_name] = str(value)

def clear_screen():
    """Nettoie l'écran du terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def create_directory(directory_path, mode=0o755):
    """
    Crée un répertoire avec les permissions spécifiées
    
    Args:
        directory_path (str): Chemin du répertoire
        mode (int): Permissions octales
        
    Returns:
        bool: True si créé avec succès
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True, mode=mode)
        return True
    except Exception as e:
        logger.error(f"Erreur création répertoire {directory_path}: {e}")
        return False

def backup_file(file_path, backup_suffix=None):
    """
    Crée une sauvegarde d'un fichier
    
    Args:
        file_path (str): Chemin du fichier à sauvegarder
        backup_suffix (str): Suffixe pour le backup (défaut: timestamp)
        
    Returns:
        str: Chemin du fichier de backup ou None
    """
    try:
        import shutil
        import time
        
        if not os.path.exists(file_path):
            return None
        
        if backup_suffix is None:
            backup_suffix = f"backup.{int(time.time())}"
        
        backup_path = f"{file_path}.{backup_suffix}"
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"Backup créé: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"Erreur création backup {file_path}: {e}")
        return None

def restore_file(backup_path, original_path):
    """
    Restaure un fichier depuis un backup
    
    Args:
        backup_path (str): Chemin du backup
        original_path (str): Chemin du fichier original
        
    Returns:
        bool: True si restauré avec succès
    """
    try:
        import shutil
        
        if not os.path.exists(backup_path):
            return False
        
        shutil.copy2(backup_path, original_path)
        logger.info(f"Fichier restauré: {original_path}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur restauration {backup_path}: {e}")
        return False

def get_disk_usage(path="/"):
    """
    Retourne l'utilisation disque d'un chemin
    
    Args:
        path (str): Chemin à analyser
        
    Returns:
        dict: Informations sur l'espace disque
    """
    try:
        stat_result = os.statvfs(path)
        
        # Taille des blocs
        block_size = stat_result.f_frsize
        
        # Calculs
        total_blocks = stat_result.f_blocks
        free_blocks = stat_result.f_bavail
        used_blocks = total_blocks - stat_result.f_bfree
        
        total_bytes = total_blocks * block_size
        free_bytes = free_blocks * block_size
        used_bytes = used_blocks * block_size
        
        usage_percent = (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
        
        return {
            'path': path,
            'total': total_bytes,
            'used': used_bytes,
            'free': free_bytes,
            'usage_percent': usage_percent
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse disque {path}: {e}")
        return None

def get_process_info(pid=None):
    """
    Retourne les informations sur un processus
    
    Args:
        pid (int): PID du processus (défaut: processus courant)
        
    Returns:
        dict: Informations sur le processus
    """
    try:
        if pid is None:
            pid = os.getpid()
        
        # Informations de base
        process_info = {
            'pid': pid,
            'ppid': None,
            'uid': None,
            'gid': None,
            'command': None,
            'cwd': None
        }
        
        # Lecture des informations depuis /proc
        proc_path = f"/proc/{pid}"
        
        if os.path.exists(proc_path):
            # PPID
            try:
                with open(f"{proc_path}/stat", 'r') as f:
                    stat_data = f.read().split()
                    if len(stat_data) > 3:
                        process_info['ppid'] = int(stat_data[3])
            except Exception:
                pass
            
            # UID/GID
            try:
                with open(f"{proc_path}/status", 'r') as f:
                    for line in f:
                        if line.startswith('Uid:'):
                            process_info['uid'] = int(line.split()[1])
                        elif line.startswith('Gid:'):
                            process_info['gid'] = int(line.split()[1])
            except Exception:
                pass
            
            # Commande
            try:
                with open(f"{proc_path}/cmdline", 'r') as f:
                    cmdline = f.read().replace('\0', ' ').strip()
                    process_info['command'] = cmdline if cmdline else None
            except Exception:
                pass
            
            # Répertoire courant
            try:
                process_info['cwd'] = os.readlink(f"{proc_path}/cwd")
            except Exception:
                pass
        
        return process_info
        
    except Exception as e:
        logger.error(f"Erreur infos processus {pid}: {e}")
        return None

def kill_process(pid, signal=15):
    """
    Tue un processus
    
    Args:
        pid (int): PID du processus
        signal (int): Signal à envoyer (défaut: SIGTERM)
        
    Returns:
        bool: True si réussi
    """
    try:
        os.kill(pid, signal)
        return True
    except Exception as e:
        logger.error(f"Erreur kill processus {pid}: {e}")
        return False

def find_processes_by_name(process_name):
    """
    Trouve les processus par nom
    
    Args:
        process_name (str): Nom du processus à chercher
        
    Returns:
        list: Liste des PIDs trouvés
    """
    try:
        result = run_command(['pgrep', process_name])
        if result['success']:
            pids = []
            for line in result['output'].split('\n'):
                if line.strip().isdigit():
                    pids.append(int(line.strip()))
            return pids
        
        # Méthode alternative
        pids = []
        for pid_dir in os.listdir('/proc'):
            if pid_dir.isdigit():
                try:
                    with open(f"/proc/{pid_dir}/comm", 'r') as f:
                        comm = f.read().strip()
                        if process_name in comm:
                            pids.append(int(pid_dir))
                except Exception:
                    continue
        
        return pids
        
    except Exception as e:
        logger.error(f"Erreur recherche processus {process_name}: {e}")
        return []

def get_network_interfaces():
    """
    Retourne les interfaces réseau
    
    Returns:
        list: Liste des interfaces réseau
    """
    try:
        result = run_command(['ip', 'link', 'show'])
        if result['success']:
            interfaces = []
            for line in result['output'].split('\n'):
                if ': ' in line and not line.startswith(' '):
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        interface_name = parts[1].split('@')[0]  # Supprime les alias
                        interfaces.append(interface_name)
            return interfaces
        
        # Méthode alternative
        try:
            interfaces = os.listdir('/sys/class/net/')
            return [iface for iface in interfaces if iface != 'lo']
        except Exception:
            return ['eth0', 'wlan0']  # Défaut
        
    except Exception as e:
        logger.error(f"Erreur récupération interfaces: {e}")
        return []

def get_listening_ports():
    """
    Retourne les ports en écoute
    
    Returns:
        list: Liste des ports en écoute
    """
    try:
        listening_ports = []
        
        # TCP
        result = run_command(['ss', '-tlnp'])
        if result['success']:
            for line in result['output'].split('\n')[1:]:  # Skip header
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        local_addr = parts[3]
                        if ':' in local_addr:
                            port = local_addr.split(':')[-1]
                            if port.isdigit():
                                listening_ports.append({
                                    'port': int(port),
                                    'protocol': 'tcp',
                                    'address': local_addr
                                })
        
        # UDP
        result = run_command(['ss', '-ulnp'])
        if result['success']:
            for line in result['output'].split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        local_addr = parts[3]
                        if ':' in local_addr:
                            port = local_addr.split(':')[-1]
                            if port.isdigit():
                                listening_ports.append({
                                    'port': int(port),
                                    'protocol': 'udp',
                                    'address': local_addr
                                })
        
        return listening_ports
        
    except Exception as e:
        logger.error(f"Erreur récupération ports: {e}")
        return []

def check_internet_connectivity(host="8.8.8.8", timeout=3):
    """
    Vérifie la connectivité internet
    
    Args:
        host (str): Hôte à tester
        timeout (int): Timeout en secondes
        
    Returns:
        bool: True si connecté
    """
    try:
        result = run_command(['ping', '-c', '1', '-W', str(timeout), host], timeout=timeout+1)
        return result['success']
    except Exception:
        return False

def get_mounted_filesystems():
    """
    Retourne les systèmes de fichiers montés
    
    Returns:
        list: Liste des points de montage
    """
    try:
        filesystems = []
        
        result = run_command(['mount'])
        if result['success']:
            for line in result['output'].split('\n'):
                if ' on ' in line and ' type ' in line:
                    parts = line.split(' on ')
                    if len(parts) >= 2:
                        device = parts[0]
                        rest = parts[1].split(' type ')
                        if len(rest) >= 2:
                            mountpoint = rest[0]
                            fstype_and_options = rest[1]
                            fstype = fstype_and_options.split()[0]
                            
                            filesystems.append({
                                'device': device,
                                'mountpoint': mountpoint,
                                'fstype': fstype
                            })
        
        return filesystems
        
    except Exception as e:
        logger.error(f"Erreur récupération filesystems: {e}")
        return []