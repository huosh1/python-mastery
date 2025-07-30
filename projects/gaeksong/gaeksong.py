#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gaeksong - Outil de reconnaissance active et passive
Point d'entrée principal
"""

import argparse
import sys
import os
from datetime import datetime

# Import des modules
from modules.passive import whois_lookup, dns_lookup, brute_force_subdomains
from modules.active import ping_sweep, port_scan, banner_grab
from modules.export import export_to_json
from modules.utils import log, validate_domain, print_colored

def setup_args():
    """Configuration des arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Gaeksong - Outil de reconnaissance active et passive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  Reconnaissance passive:
    python3 gaeksong.py passive --domain example.com --whois --dns --output results/example.json
    
  Reconnaissance active:
    python3 gaeksong.py active --target 192.168.1.1 --ports 22,80,443 --banner --output results/scan.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande passive
    passive_parser = subparsers.add_parser('passive', help='Reconnaissance passive')
    passive_parser.add_argument('--domain', required=True, help='Domaine cible à analyser')
    passive_parser.add_argument('--whois', action='store_true', help='Active la récupération WHOIS')
    passive_parser.add_argument('--dns', action='store_true', help='Active la récupération DNS')
    passive_parser.add_argument('--dns-brute', metavar='WORDLIST', help='Lance un bruteforce des sous-domaines')
    passive_parser.add_argument('--output', help='Fichier de sortie JSON')
    
    # Commande active
    active_parser = subparsers.add_parser('active', help='Reconnaissance active')
    active_parser.add_argument('--target', required=True, help='Adresse IP cible')
    active_parser.add_argument('--ports', help='Liste des ports séparés par des virgules (ex: 22,80,443)')
    active_parser.add_argument('--ping-sweep', metavar='CIDR', help='Ping sweep sur une plage réseau')
    active_parser.add_argument('--banner', action='store_true', help='Active le banner grabbing')
    active_parser.add_argument('--output', help='Fichier de sortie JSON')
    
    return parser

def run_passive_recon(args):
    """Exécute la reconnaissance passive"""
    domain = args.domain
    results = {
        'type': 'passive',
        'target': domain,
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }
    
    # Validation du domaine
    if not validate_domain(domain):
        print_colored(f"Erreur: Domaine invalide '{domain}'", "red")
        return None
    
    print_colored(f"[+] Démarrage de la reconnaissance passive pour: {domain}", "green")
    
    # WHOIS
    if args.whois:
        print_colored("[*] Récupération des données WHOIS...", "blue")
        whois_data = whois_lookup(domain)
        results['data']['whois'] = whois_data
        log(f"WHOIS lookup effectué pour {domain}", "info")
    
    # DNS
    if args.dns:
        print_colored("[*] Récupération des enregistrements DNS...", "blue")
        dns_data = dns_lookup(domain)
        results['data']['dns'] = dns_data
        log(f"DNS lookup effectué pour {domain}", "info")
    
    # Bruteforce sous-domaines
    if args.dns_brute:
        print_colored(f"[*] Bruteforce des sous-domaines avec {args.dns_brute}...", "blue")
        subdomains = brute_force_subdomains(domain, args.dns_brute)
        results['data']['subdomains'] = subdomains
        log(f"Bruteforce sous-domaines effectué pour {domain}", "info")
    
    return results

def run_active_recon(args):
    """Exécute la reconnaissance active"""
    target = args.target
    results = {
        'type': 'active',
        'target': target,
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }
    
    print_colored(f"[+] Démarrage de la reconnaissance active pour: {target}", "green")
    
    # Ping sweep
    if args.ping_sweep:
        print_colored(f"[*] Ping sweep sur {args.ping_sweep}...", "blue")
        alive_hosts = ping_sweep(args.ping_sweep)
        results['data']['ping_sweep'] = alive_hosts
        log(f"Ping sweep effectué sur {args.ping_sweep}", "info")
    
    # Port scan
    if args.ports:
        ports = [int(p.strip()) for p in args.ports.split(',')]
        print_colored(f"[*] Scan des ports {args.ports} sur {target}...", "blue")
        open_ports = port_scan(target, ports)
        results['data']['port_scan'] = open_ports
        log(f"Port scan effectué sur {target}", "info")
        
        # Banner grabbing
        if args.banner and open_ports:
            print_colored("[*] Banner grabbing sur les ports ouverts...", "blue")
            banners = {}
            for port in open_ports:
                banner = banner_grab(target, port)
                if banner:
                    banners[port] = banner
            results['data']['banners'] = banners
            log(f"Banner grabbing effectué sur {target}", "info")
    
    return results

def main():
    """Fonction principale"""
    parser = setup_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Création du dossier results s'il n'existe pas
    os.makedirs('results', exist_ok=True)
    
    results = None
    
    # Exécution selon la commande
    if args.command == 'passive':
        results = run_passive_recon(args)
    elif args.command == 'active':
        results = run_active_recon(args)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Export des résultats
    if results:
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/{args.command}_{results['target']}_{timestamp}.json"
        
        if export_to_json(results, output_path):
            print_colored(f"[+] Résultats sauvegardés dans: {output_path}", "green")
        else:
            print_colored(f"[-] Erreur lors de la sauvegarde", "red")
    
    print_colored("[+] Reconnaissance terminée!", "green")

if __name__ == "__main__":
    main()