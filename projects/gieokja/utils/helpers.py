"""
Fonctions utilitaires pour Gieokja
"""

import os
import re
import subprocess
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


def truncate_output(output: str, max_lines: int = 100) -> str:
    """Tronquer la sortie si elle est trop longue"""
    lines = output.split('\n')
    
    if len(lines) <= max_lines:
        return output
    
    # Garder le début et la fin
    keep_start = max_lines // 2
    keep_end = max_lines - keep_start
    
    truncated = lines[:keep_start]
    truncated.append(f"\n... [{len(lines) - max_lines} lignes tronquées] ...\n")
    truncated.extend(lines[-keep_end:])
    
    return '\n'.join(truncated)


def format_duration(duration: timedelta) -> str:
    """Formater une durée de manière lisible"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return ' '.join(parts)


def extract_ips(text: str) -> List[str]:
    """Extraire les adresses IP d'un texte"""
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(ip_pattern, text)
    
    # Filtrer les IPs non valides et locales
    valid_ips = []
    for ip in ips:
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            if not ip.startswith(('127.', '0.', '255.')):
                valid_ips.append(ip)
    
    return list(set(valid_ips))


def extract_urls(text: str) -> List[str]:
    """Extraire les URLs d'un texte"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))


def extract_hashes(text: str) -> Dict[str, List[str]]:
    """Extraire les hashes potentiels d'un texte"""
    hash_patterns = {
        'MD5': r'\b[a-fA-F0-9]{32}\b',
        'SHA1': r'\b[a-fA-F0-9]{40}\b',
        'SHA256': r'\b[a-fA-F0-9]{64}\b',
        'NTLM': r'\b[a-fA-F0-9]{32}:[a-fA-F0-9]{32}\b'
    }
    
    results = {}
    for hash_type, pattern in hash_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            results[hash_type] = list(set(matches))
    
    return results


def get_system_info() -> Dict[str, str]:
    """Obtenir les informations système"""
    info = {
        'os': os.name,
        'platform': os.uname().sysname,
        'hostname': os.uname().nodename,
        'user': os.getenv('USER', 'unknown'),
        'home': os.path.expanduser('~'),
        'cwd': os.getcwd(),
        'shell': os.getenv('SHELL', 'unknown')
    }
    
    # Essayer d'obtenir l'IP locale
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
    except:
        info['local_ip'] = 'unknown'
    
    return info


def run_command(command: str, timeout: int = 30) -> tuple:
    """Exécuter une commande et retourner (stdout, stderr, return_code)"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timeout après {timeout} secondes", -1
    except Exception as e:
        return "", str(e), -1


def sanitize_filename(filename: str) -> str:
    """Nettoyer un nom de fichier pour qu'il soit valide"""
    # Remplacer les caractères invalides
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limiter la longueur
    max_length = 200
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length - len(ext)] + ext
    
    return filename


def create_backup(file_path: str) -> Optional[str]:
    """Créer une sauvegarde d'un fichier"""
    path = Path(file_path)
    
    if not path.exists():
        return None
    
    # Créer le nom de la sauvegarde
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    backup_path = path.parent / backup_name
    
    try:
        import shutil
        shutil.copy2(path, backup_path)
        return str(backup_path)
    except Exception:
        return None


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
    """Calculer le hash d'un fichier"""
    hash_algo = getattr(hashlib, algorithm.lower(), None)
    if not hash_algo:
        return None
    
    try:
        hash_obj = hash_algo()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None


def parse_nmap_output(output: str) -> Dict[str, Any]:
    """Parser basique de la sortie nmap"""
    result = {
        'hosts': [],
        'open_ports': [],
        'services': []
    }
    
    # Extraire les hôtes
    host_pattern = r'Nmap scan report for (.+?)(?:\s+\((.+?)\))?'
    hosts = re.findall(host_pattern, output)
    result['hosts'] = [{'name': h[0], 'ip': h[1] if h[1] else h[0]} for h in hosts]
    
    # Extraire les ports ouverts
    port_pattern = r'(\d+)/(tcp|udp)\s+open\s+(\S+)(?:\s+(.+))?'
    ports = re.findall(port_pattern, output)
    
    for port, proto, service, version in ports:
        port_info = {
            'port': int(port),
            'protocol': proto,
            'service': service,
            'version': version.strip() if version else ''
        }
        result['open_ports'].append(port_info)
        
        if service not in result['services']:
            result['services'].append(service)
    
    return result


def is_tool_available(tool_name: str) -> bool:
    """Vérifier si un outil est disponible dans le PATH"""
    try:
        subprocess.run(
            ['which', tool_name],
            capture_output=True,
            check=True
        )
        return True
    except:
        return False


def get_available_tools() -> List[str]:
    """Obtenir la liste des outils CTF disponibles"""
    common_tools = [
        'nmap', 'gobuster', 'ffuf', 'nikto', 'sqlmap',
        'hydra', 'john', 'hashcat', 'metasploit', 'burpsuite',
        'dirb', 'dirbuster', 'wfuzz', 'netcat', 'nc',
        'python', 'python3', 'ruby', 'perl', 'gcc',
        'gdb', 'radare2', 'objdump', 'strings', 'file',
        'binwalk', 'exiftool', 'steghide', 'foremost'
    ]
    
    available = []
    for tool in common_tools:
        if is_tool_available(tool):
            available.append(tool)
    
    return available


def merge_session_data(session1: Dict, session2: Dict) -> Dict:
    """Fusionner deux sessions de données"""
    merged = session1.copy()
    
    # Fusionner les listes
    for key in ['commands', 'flags', 'notes', 'todos']:
        if key in session2:
            if key not in merged:
                merged[key] = []
            merged[key].extend(session2[key])
    
    # Garder les valeurs les plus récentes pour les autres champs
    for key in ['target_ip', 'current_user', 'current_host']:
        if key in session2 and session2[key]:
            merged[key] = session2[key]
    
    return merged


def export_to_json(data: Dict, output_file: str) -> bool:
    """Exporter des données en JSON"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        return True
    except Exception:
        return False


def import_from_json(input_file: str) -> Optional[Dict]:
    """Importer des données depuis JSON"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None