#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de reconnaissance active
Fonctions pour ping sweep, port scan et banner grabbing
"""

import socket
import threading
import time
import subprocess
import ipaddress
from modules.utils import log, print_colored

def ping_host(ip, results, lock):
    """
    Ping un hôte spécifique
    
    Args:
        ip (str): Adresse IP à pinger
        results (list): Liste partagée pour stocker les résultats
        lock: Verrou pour l'accès concurrent
    """
    try:
        # Utilisation de ping système (compatible Linux/Windows)
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', str(ip)] if subprocess.sys.platform != 'win32' 
            else ['ping', '-n', '1', '-w', '1000', str(ip)],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if result.returncode == 0:
            with lock:
                results.append({
                    'ip': str(ip),
                    'status': 'alive',
                    'response_time': 'N/A'  # TODO: extraire le temps de réponse
                })
            print_colored(f"[+] {ip} est en ligne", "green")
            
    except subprocess.TimeoutExpired:
        log(f"Timeout ping pour {ip}", "warning")
    except Exception as e:
        log(f"Erreur ping pour {ip}: {str(e)}", "error")

def ping_sweep(cidr_range, max_threads=50):
    """
    Effectue un ping sweep sur une plage réseau
    
    Args:
        cidr_range (str): Plage réseau en notation CIDR (ex: 192.168.1.0/24)
        max_threads (int): Nombre maximum de threads
        
    Returns:
        list: Liste des hôtes actifs
    """
    try:
        network = ipaddress.ip_network(cidr_range, strict=False)
        print_colored(f"[*] Ping sweep sur {cidr_range} ({network.num_addresses} adresses)", "blue")
        
    except ValueError as e:
        print_colored(f"[-] Plage réseau invalide: {e}", "red")
        return []
    
    results = []
    lock = threading.Lock()
    threads = []
    semaphore = threading.Semaphore(max_threads)
    
    def worker(ip):
        with semaphore:
            ping_host(ip, results, lock)
    
    # Ping de chaque adresse du réseau
    for ip in network.hosts():
        thread = threading.Thread(target=worker, args=(ip,))
        threads.append(thread)
        thread.start()
        time.sleep(0.01)  # Petit délai
    
    # Attente de tous les threads
    for thread in threads:
        thread.join()
    
    print_colored(f"[+] Ping sweep terminé: {len(results)}/{network.num_addresses} hôtes actifs", "green")
    log(f"Ping sweep sur {cidr_range}: {len(results)} hôtes actifs", "info")
    
    return results

def scan_port(ip, port, results, lock, timeout=1):
    """
    Scanne un port spécifique sur une IP
    
    Args:
        ip (str): Adresse IP cible
        port (int): Port à scanner
        results (list): Liste partagée pour stocker les résultats
        lock: Verrou pour l'accès concurrent
        timeout (int): Timeout de connexion
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            with lock:
                results.append({
                    'port': port,
                    'status': 'open',
                    'service': get_service_name(port)
                })
            print_colored(f"[+] {ip}:{port} ouvert ({get_service_name(port)})", "green")
        
        sock.close()
        
    except Exception as e:
        log(f"Erreur scan port {ip}:{port}: {str(e)}", "error")

def get_service_name(port):
    """
    Retourne le nom du service associé à un port
    
    Args:
        port (int): Numéro du port
        
    Returns:
        str: Nom du service
    """
    common_ports = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        135: 'RPC',
        139: 'NetBIOS',
        143: 'IMAP',
        443: 'HTTPS',
        445: 'SMB',
        993: 'IMAPS',
        995: 'POP3S',
        1433: 'MSSQL',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        8080: 'HTTP-Alt'
    }
    
    return common_ports.get(port, 'Unknown')

def port_scan(ip, ports, max_threads=50):
    """
    Effectue un scan de ports sur une IP
    
    Args:
        ip (str): Adresse IP cible
        ports (list): Liste des ports à scanner
        max_threads (int): Nombre maximum de threads
        
    Returns:
        list: Liste des ports ouverts
    """
    print_colored(f"[*] Scan de {len(ports)} ports sur {ip}", "blue")
    
    results = []
    lock = threading.Lock()
    threads = []
    semaphore = threading.Semaphore(max_threads)
    
    def worker(port):
        with semaphore:
            scan_port(ip, port, results, lock)
    
    # Scan de chaque port
    for port in ports:
        thread = threading.Thread(target=worker, args=(port,))
        threads.append(thread)
        thread.start()
        time.sleep(0.001)  # Petit délai
    
    # Attente de tous les threads
    for thread in threads:
        thread.join()
    
    print_colored(f"[+] Scan terminé: {len(results)}/{len(ports)} ports ouverts", "green")
    log(f"Port scan sur {ip}: {len(results)} ports ouverts", "info")
    
    return results

def banner_grab(ip, port, timeout=3):
    """
    Effectue un banner grabbing sur un port
    
    Args:
        ip (str): Adresse IP cible
        port (int): Port cible
        timeout (int): Timeout de connexion
        
    Returns:
        dict: Informations du banner ou None
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        sock.connect((ip, port))
        
        # Envoi d'une requête basique selon le port
        if port == 80 or port == 8080:
            sock.send(b"GET / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
        elif port == 443:
            # Pour HTTPS, on ne peut pas faire de requête simple sans SSL
            pass
        elif port == 25:  # SMTP
            pass  # Le serveur envoie généralement un banner automatiquement
        elif port == 21:  # FTP
            pass  # Banner automatique
        elif port == 22:  # SSH
            pass  # Banner automatique
        else:
            # Tentative générique
            sock.send(b"\r\n")
        
        # Réception du banner
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        
        sock.close()
        
        if banner:
            banner_info = {
                'port': port,
                'banner': banner,
                'service': get_service_name(port)
            }
            
            print_colored(f"[+] Banner {ip}:{port} -> {banner[:50]}{'...' if len(banner) > 50 else ''}", "green")
            log(f"Banner grab réussi sur {ip}:{port}", "info")
            
            return banner_info
        
    except socket.timeout:
        log(f"Timeout banner grab {ip}:{port}", "warning")
    except Exception as e:
        log(f"Erreur banner grab {ip}:{port}: {str(e)}", "error")
    
    return None