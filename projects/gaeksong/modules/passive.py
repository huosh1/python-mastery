#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de reconnaissance passive
Fonctions pour WHOIS, DNS et bruteforce de sous-domaines
"""

import whois
import dns.resolver
import dns.exception
import socket
import threading
import time
from modules.utils import log, print_colored, load_wordlist

def whois_lookup(domain):
    """
    Effectue une requête WHOIS sur un domaine
    
    Args:
        domain (str): Le domaine à analyser
        
    Returns:
        dict: Informations WHOIS ou None en cas d'erreur
    """
    try:
        w = whois.whois(domain)
        
        # Extraction des informations principales
        whois_data = {
            'domain_name': w.domain_name,
            'registrar': w.registrar,
            'creation_date': str(w.creation_date) if w.creation_date else None,
            'expiration_date': str(w.expiration_date) if w.expiration_date else None,
            'updated_date': str(w.updated_date) if w.updated_date else None,
            'name_servers': w.name_servers if w.name_servers else [],
            'status': w.status if w.status else [],
            'emails': w.emails if w.emails else [],
            'org': w.org if hasattr(w, 'org') else None,
            'country': w.country if hasattr(w, 'country') else None
        }
        
        log(f"WHOIS lookup réussi pour {domain}", "info")
        return whois_data
        
    except Exception as e:
        log(f"Erreur WHOIS pour {domain}: {str(e)}", "error")
        print_colored(f"[-] Erreur WHOIS: {str(e)}", "red")
        return None

def dns_lookup(domain):
    """
    Effectue des requêtes DNS pour différents types d'enregistrements
    
    Args:
        domain (str): Le domaine à analyser
        
    Returns:
        dict: Enregistrements DNS trouvés
    """
    dns_data = {
        'A': [],
        'AAAA': [],
        'MX': [],
        'NS': [],
        'TXT': [],
        'CNAME': [],
        'SOA': []
    }
    
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            for answer in answers:
                if record_type == 'MX':
                    dns_data[record_type].append({
                        'priority': answer.preference,
                        'exchange': str(answer.exchange)
                    })
                elif record_type == 'SOA':
                    dns_data[record_type].append({
                        'mname': str(answer.mname),
                        'rname': str(answer.rname),
                        'serial': answer.serial,
                        'refresh': answer.refresh,
                        'retry': answer.retry,
                        'expire': answer.expire,
                        'minimum': answer.minimum
                    })
                else:
                    dns_data[record_type].append(str(answer))
                    
        except dns.resolver.NXDOMAIN:
            log(f"Domaine {domain} n'existe pas pour {record_type}", "warning")
        except dns.resolver.NoAnswer:
            log(f"Pas de réponse {record_type} pour {domain}", "info")
        except Exception as e:
            log(f"Erreur DNS {record_type} pour {domain}: {str(e)}", "error")
    
    log(f"DNS lookup effectué pour {domain}", "info")
    return dns_data

def check_subdomain(subdomain, domain, results, lock):
    """
    Vérifie l'existence d'un sous-domaine
    
    Args:
        subdomain (str): Le sous-domaine à tester
        domain (str): Le domaine principal
        results (list): Liste partagée pour stocker les résultats
        lock: Verrou pour l'accès concurrent à la liste
    """
    full_domain = f"{subdomain}.{domain}"
    
    try:
        # Tentative de résolution DNS
        answer = dns.resolver.resolve(full_domain, 'A')
        ips = [str(ip) for ip in answer]
        
        with lock:
            results.append({
                'subdomain': full_domain,
                'ips': ips,
                'status': 'found'
            })
            
        print_colored(f"[+] Trouvé: {full_domain} -> {', '.join(ips)}", "green")
        
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        # Sous-domaine n'existe pas
        pass
    except Exception as e:
        log(f"Erreur lors de la vérification de {full_domain}: {str(e)}", "error")

def brute_force_subdomains(domain, wordlist_path, max_threads=50):
    """
    Effectue un bruteforce des sous-domaines
    
    Args:
        domain (str): Le domaine principal
        wordlist_path (str): Chemin vers le fichier wordlist
        max_threads (int): Nombre maximum de threads
        
    Returns:
        list: Liste des sous-domaines trouvés
    """
    print_colored(f"[*] Chargement de la wordlist: {wordlist_path}", "blue")
    
    # Chargement de la wordlist
    wordlist = load_wordlist(wordlist_path)
    if not wordlist:
        print_colored(f"[-] Impossible de charger la wordlist: {wordlist_path}", "red")
        return []
    
    print_colored(f"[*] {len(wordlist)} mots chargés, démarrage du bruteforce...", "blue")
    
    results = []
    lock = threading.Lock()
    threads = []
    
    # Limitation du nombre de threads actifs
    semaphore = threading.Semaphore(max_threads)
    
    def worker(subdomain):
        with semaphore:
            check_subdomain(subdomain, domain, results, lock)
    
    # Création des threads
    for subdomain in wordlist:
        thread = threading.Thread(target=worker, args=(subdomain.strip(),))
        threads.append(thread)
        thread.start()
        
        # Petit délai pour éviter de surcharger
        time.sleep(0.01)
    
    # Attente de tous les threads
    for thread in threads:
        thread.join()
    
    print_colored(f"[+] Bruteforce terminé: {len(results)} sous-domaines trouvés", "green")
    log(f"Bruteforce terminé pour {domain}: {len(results)} sous-domaines", "info")
    
    return results