#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface CLI pour Seullipeo
Gestion des arguments en ligne de commande
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path

from utils.display import print_colored, show_banner
from utils.logger import get_logger
from utils.system import is_root
from exploits import get_available_modules, load_module

logger = get_logger(__name__)

class SeullipeoCLI:
    """Classe principale pour l'interface CLI"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'modules': {},
            'summary': {
                'total_vulns': 0,
                'exploited': 0,
                'failed': 0
            }
        }
        self.modules_to_run = []
        self.scan_only = False
        self.exploit_only = False
        self.aggressive = False
        self.output_file = None
        self.json_output = None
    
    def setup_parser(self):
        """Configure le parser d'arguments"""
        parser = argparse.ArgumentParser(
            description="Seullipeo CLI - Framework d'escalade de privilèges",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Modules disponibles
        modules_group = parser.add_argument_group('Modules d\'exploitation')
        modules_group.add_argument('--cron', action='store_true',
                                 help='Active le module cron')
        modules_group.add_argument('--suid', action='store_true',
                                 help='Active le module SUID')
        modules_group.add_argument('--passwd', action='store_true',
                                 help='Active le module passwd writable')
        modules_group.add_argument('--all-modules', action='store_true',
                                 help='Active tous les modules disponibles')
        
        # Modes d'exécution
        execution_group = parser.add_argument_group('Modes d\'exécution')
        execution_group.add_argument('--scan', action='store_true',
                                   help='Effectue uniquement un scan')
        execution_group.add_argument('--exploit', action='store_true',
                                   help='Lance directement les exploits')
        execution_group.add_argument('--aggressive', action='store_true',
                                   help='Combine scan + exploit sur tous les modules')
        
        # Options de sortie
        output_group = parser.add_argument_group('Options de sortie')
        output_group.add_argument('--output', metavar='FILE',
                                help='Fichier de sortie texte')
        output_group.add_argument('--json', metavar='FILE',
                                help='Fichier de sortie JSON')
        output_group.add_argument('--verbose', '-v', action='store_true',
                                help='Mode verbeux')
        
        # Utilitaires
        utils_group = parser.add_argument_group('Utilitaires')
        utils_group.add_argument('--list-modules', action='store_true',
                               help='Liste tous les modules disponibles')
        utils_group.add_argument('--banner', action='store_true',
                               help='Affiche la bannière')
        
        return parser
    
    def list_modules(self):
        """Liste tous les modules disponibles"""
        print_colored("\n[*] Modules disponibles:", "blue")
        modules = get_available_modules()
        
        for module_name, module_info in modules.items():
            status = "✓" if module_info.get('available', True) else "✗"
            print_colored(f"  {status} {module_name:<15} - {module_info.get('description', 'N/A')}", "white")
        
        print_colored(f"\n[*] Total: {len(modules)} modules", "green")
    
    def parse_modules(self, args):
        """Parse les modules à exécuter depuis les arguments"""
        modules = []
        
        if args.all_modules:
            modules = list(get_available_modules().keys())
        else:
            if args.cron:
                modules.append('cron')
            if args.suid:
                modules.append('suid')
            if args.passwd:
                modules.append('passwd_writable')
        
        return modules
    
    def run_module(self, module_name, scan_only=False):
        """Exécute un module spécifique"""
        print_colored(f"\n[*] Chargement du module: {module_name}", "blue")
        
        try:
            module = load_module(module_name)
            if not module:
                print_colored(f"[-] Impossible de charger le module: {module_name}", "red")
                return False
            
            # Initialisation du module
            instance = module.Module()
            
            # Résultats du module
            module_results = {
                'name': module_name,
                'scan_results': [],
                'exploit_results': [],
                'errors': []
            }
            
            # Phase de scan
            print_colored(f"[*] Scan avec {module_name}...", "yellow")
            try:
                vulns = instance.scan()
                module_results['scan_results'] = vulns
                
                if vulns:
                    print_colored(f"[+] {len(vulns)} vulnérabilité(s) trouvée(s)", "green")
                    for i, vuln in enumerate(vulns, 1):
                        print_colored(f"    {i}. {vuln.get('description', 'N/A')}", "white")
                else:
                    print_colored(f"[-] Aucune vulnérabilité trouvée", "yellow")
                
            except Exception as e:
                error = f"Erreur lors du scan: {str(e)}"
                module_results['errors'].append(error)
                print_colored(f"[-] {error}", "red")
                logger.error(f"Erreur scan {module_name}: {e}")
            
            # Phase d'exploitation (si demandé)
            if not scan_only and module_results['scan_results']:
                print_colored(f"[*] Exploitation avec {module_name}...", "yellow")
                
                try:
                    exploit_results = instance.exploit_all()
                    module_results['exploit_results'] = exploit_results
                    
                    success_count = sum(1 for r in exploit_results if r.get('success', False))
                    if success_count > 0:
                        print_colored(f"[+] {success_count} exploit(s) réussi(s)", "green")
                    else:
                        print_colored(f"[-] Aucun exploit réussi", "red")
                        
                except Exception as e:
                    error = f"Erreur lors de l'exploitation: {str(e)}"
                    module_results['errors'].append(error)
                    print_colored(f"[-] {error}", "red")
                    logger.error(f"Erreur exploit {module_name}: {e}")
            
            # Sauvegarde des résultats
            self.results['modules'][module_name] = module_results
            self.results['summary']['total_vulns'] += len(module_results['scan_results'])
            
            return True
            
        except Exception as e:
            print_colored(f"[-] Erreur critique avec le module {module_name}: {str(e)}", "red")
            logger.error(f"Erreur critique {module_name}: {e}")
            return False
    
    def save_results(self):
        """Sauvegarde les résultats"""
        # Calcul du résumé final
        for module_results in self.results['modules'].values():
            for exploit_result in module_results.get('exploit_results', []):
                if exploit_result.get('success', False):
                    self.results['summary']['exploited'] += 1
                else:
                    self.results['summary']['failed'] += 1
        
        # Sauvegarde texte
        if self.output_file:
            try:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("SEULLIPEO - RAPPORT D'ESCALADE DE PRIVILÈGES\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Timestamp: {self.results['timestamp']}\n")
                    f.write(f"Version: {self.results['version']}\n\n")
                    
                    f.write("RÉSUMÉ:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Vulnérabilités trouvées: {self.results['summary']['total_vulns']}\n")
                    f.write(f"Exploits réussis: {self.results['summary']['exploited']}\n")
                    f.write(f"Exploits échoués: {self.results['summary']['failed']}\n\n")
                    
                    for module_name, module_data in self.results['modules'].items():
                        f.write(f"MODULE: {module_name.upper()}\n")
                        f.write("-" * 30 + "\n")
                        
                        # Résultats de scan
                        if module_data['scan_results']:
                            f.write("Vulnérabilités détectées:\n")
                            for i, vuln in enumerate(module_data['scan_results'], 1):
                                f.write(f"  {i}. {vuln.get('description', 'N/A')}\n")
                                if vuln.get('path'):
                                    f.write(f"     Chemin: {vuln['path']}\n")
                        else:
                            f.write("Aucune vulnérabilité détectée.\n")
                        
                        # Résultats d'exploitation
                        if module_data['exploit_results']:
                            f.write("\nRésultats d'exploitation:\n")
                            for result in module_data['exploit_results']:
                                status = "SUCCÈS" if result.get('success') else "ÉCHEC"
                                f.write(f"  - {status}: {result.get('description', 'N/A')}\n")
                        
                        # Erreurs
                        if module_data['errors']:
                            f.write("\nErreurs:\n")
                            for error in module_data['errors']:
                                f.write(f"  - {error}\n")
                        
                        f.write("\n")
                
                print_colored(f"[+] Résultats sauvegardés dans: {self.output_file}", "green")
                
            except Exception as e:
                print_colored(f"[-] Erreur sauvegarde texte: {str(e)}", "red")
        
        # Sauvegarde JSON
        if self.json_output:
            try:
                with open(self.json_output, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
                
                print_colored(f"[+] Résultats JSON sauvegardés dans: {self.json_output}", "green")
                
            except Exception as e:
                print_colored(f"[-] Erreur sauvegarde JSON: {str(e)}", "red")
    
    def run(self, args):
        """Exécute le CLI avec les arguments fournis"""
        # Gestion des options utilitaires
        if args.list_modules:
            self.list_modules()
            return
        
        if args.banner:
            show_banner()
            return
        
        # Parse des modules
        self.modules_to_run = self.parse_modules(args)
        
        if not self.modules_to_run:
            print_colored("[-] Aucun module spécifié. Utilisez --help pour voir les options.", "red")
            return
        
        # Configuration des modes
        self.scan_only = args.scan and not args.exploit and not args.aggressive
        self.exploit_only = args.exploit and not args.scan
        self.aggressive = args.aggressive
        self.output_file = args.output
        self.json_output = args.json
        
        # Affichage de la bannière
        show_banner()
        
        # Vérification des privilèges
        if not is_root():
            print_colored("[!] Attention: Exécution sans privilèges root", "yellow")
        
        # Affichage de la configuration
        mode = "AGRESSIF" if self.aggressive else ("SCAN SEUL" if self.scan_only else "EXPLOITATION")
        print_colored(f"\n[*] Mode: {mode}", "blue")
        print_colored(f"[*] Modules: {', '.join(self.modules_to_run)}", "blue")
        
        # Exécution des modules
        success_count = 0
        for module_name in self.modules_to_run:
            if self.run_module(module_name, scan_only=self.scan_only):
                success_count += 1
        
        # Résumé final
        print_colored(f"\n[*] Exécution terminée: {success_count}/{len(self.modules_to_run)} modules réussis", "blue")
        print_colored(f"[*] Total vulnérabilités: {self.results['summary']['total_vulns']}", "green")
        
        if not self.scan_only:
            print_colored(f"[*] Exploits réussis: {self.results['summary']['exploited']}", "green")
        
        # Sauvegarde des résultats
        if self.output_file or self.json_output:
            self.save_results()

def main():
    """Point d'entrée principal du CLI"""
    cli = SeullipeoCLI()
    parser = cli.setup_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    cli.run(args)