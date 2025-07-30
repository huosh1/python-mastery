#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module d'export des résultats
Fonctions pour exporter en JSON et HTML
"""

import json
import os
from datetime import datetime
from modules.utils import log, print_colored

def export_to_json(data, output_path):
    """
    Exporte les données au format JSON
    
    Args:
        data (dict): Données à exporter
        output_path (str): Chemin du fichier de sortie
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Création du répertoire parent si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        log(f"Export JSON réussi: {output_path}", "info")
        return True
        
    except Exception as e:
        log(f"Erreur export JSON: {str(e)}", "error")
        print_colored(f"[-] Erreur lors de l'export JSON: {str(e)}", "red")
        return False

def export_to_html(data, output_path):
    """
    Exporte les données au format HTML
    
    Args:
        data (dict): Données à exporter
        output_path (str): Chemin du fichier de sortie
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Création du répertoire parent si nécessaire
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        html_content = generate_html_report(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        log(f"Export HTML réussi: {output_path}", "info")
        return True
        
    except Exception as e:
        log(f"Erreur export HTML: {str(e)}", "error")
        print_colored(f"[-] Erreur lors de l'export HTML: {str(e)}", "red")
        return False

def generate_html_report(data):
    """
    Génère le contenu HTML du rapport
    
    Args:
        data (dict): Données à inclure dans le rapport
        
    Returns:
        str: Contenu HTML généré
    """
    html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport Gaeksong - {target}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .success {{
            color: #27ae60;
            font-weight: bold;
        }}
        .warning {{
            color: #e67e22;
            font-weight: bold;
        }}
        .error {{
            color: #e74c3c;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .code {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 10px;
            font-family: monospace;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Rapport de Reconnaissance Gaeksong</h1>
            <p><strong>Cible:</strong> {target}</p>
            <p><strong>Type:</strong> {scan_type}</p>
            <p><strong>Date:</strong> {timestamp}</p>
        </div>
        
        {content}
        
        <div class="section">
            <h2>📊 Résumé</h2>
            <p>Rapport généré automatiquement par Gaeksong</p>
            <p><em>Outil développé à des fins éducatives et de test de sécurité autorisé uniquement.</em></p>
        </div>
    </div>
</body>
</html>
    """
    
    # Génération du contenu selon le type de scan
    content_sections = []
    
    if data['type'] == 'passive':
        content_sections.extend(generate_passive_sections(data.get('data', {})))
    elif data['type'] == 'active':
        content_sections.extend(generate_active_sections(data.get('data', {})))
    
    content = '\n'.join(content_sections)
    
    return html_template.format(
        target=data.get('target', 'N/A'),
        scan_type=data.get('type', 'N/A').title(),
        timestamp=data.get('timestamp', 'N/A'),
        content=content
    )

def generate_passive_sections(data):
    """
    Génère les sections HTML pour la reconnaissance passive
    
    Args:
        data (dict): Données de reconnaissance passive
        
    Returns:
        list: Liste des sections HTML
    """
    sections = []
    
    # Section WHOIS
    if 'whois' in data and data['whois']:
        whois_data = data['whois']
        whois_html = f"""
        <div class="section">
            <h2>🏢 Informations WHOIS</h2>
            <table>
                <tr><th>Propriété</th><th>Valeur</th></tr>
                <tr><td>Nom de domaine</td><td>{whois_data.get('domain_name', 'N/A')}</td></tr>
                <tr><td>Registrar</td><td>{whois_data.get('registrar', 'N/A')}</td></tr>
                <tr><td>Date de création</td><td>{whois_data.get('creation_date', 'N/A')}</td></tr>
                <tr><td>Date d'expiration</td><td>{whois_data.get('expiration_date', 'N/A')}</td></tr>
                <tr><td>Dernière mise à jour</td><td>{whois_data.get('updated_date', 'N/A')}</td></tr>
                <tr><td>Organisation</td><td>{whois_data.get('org', 'N/A')}</td></tr>
                <tr><td>Pays</td><td>{whois_data.get('country', 'N/A')}</td></tr>
                <tr><td>Serveurs de noms</td><td>{', '.join(whois_data.get('name_servers', [])) if whois_data.get('name_servers') else 'N/A'}</td></tr>
                <tr><td>Emails</td><td>{', '.join(whois_data.get('emails', [])) if whois_data.get('emails') else 'N/A'}</td></tr>
            </table>
        </div>
        """
        sections.append(whois_html)
    
    # Section DNS
    if 'dns' in data and data['dns']:
        dns_data = data['dns']
        dns_html = """
        <div class="section">
            <h2>🌐 Enregistrements DNS</h2>
        """
        
        for record_type, records in dns_data.items():
            if records:
                dns_html += f"<h3>Enregistrements {record_type}</h3>"
                dns_html += "<ul>"
                for record in records:
                    if isinstance(record, dict):
                        if record_type == 'MX':
                            dns_html += f"<li><strong>Priorité {record['priority']}:</strong> {record['exchange']}</li>"
                        elif record_type == 'SOA':
                            dns_html += f"<li><strong>MNAME:</strong> {record['mname']}, <strong>RNAME:</strong> {record['rname']}</li>"
                    else:
                        dns_html += f"<li>{record}</li>"
                dns_html += "</ul>"
        
        dns_html += "</div>"
        sections.append(dns_html)
    
    # Section Sous-domaines
    if 'subdomains' in data and data['subdomains']:
        subdomains = data['subdomains']
        subdomains_html = f"""
        <div class="section">
            <h2>🔍 Sous-domaines découverts ({len(subdomains)} trouvés)</h2>
            <table>
                <tr><th>Sous-domaine</th><th>Adresses IP</th><th>Statut</th></tr>
        """
        
        for subdomain in subdomains:
            ips = ', '.join(subdomain.get('ips', []))
            subdomains_html += f"""
                <tr>
                    <td>{subdomain.get('subdomain', 'N/A')}</td>
                    <td>{ips}</td>
                    <td><span class="success">{subdomain.get('status', 'N/A')}</span></td>
                </tr>
            """
        
        subdomains_html += "</table></div>"
        sections.append(subdomains_html)
    
    return sections

def generate_active_sections(data):
    """
    Génère les sections HTML pour la reconnaissance active
    
    Args:
        data (dict): Données de reconnaissance active
        
    Returns:
        list: Liste des sections HTML
    """
    sections = []
    
    # Section Ping Sweep
    if 'ping_sweep' in data and data['ping_sweep']:
        hosts = data['ping_sweep']
        ping_html = f"""
        <div class="section">
            <h2>📡 Ping Sweep ({len(hosts)} hôtes actifs)</h2>
            <table>
                <tr><th>Adresse IP</th><th>Statut</th><th>Temps de réponse</th></tr>
        """
        
        for host in hosts:
            ping_html += f"""
                <tr>
                    <td>{host.get('ip', 'N/A')}</td>
                    <td><span class="success">{host.get('status', 'N/A')}</span></td>
                    <td>{host.get('response_time', 'N/A')}</td>
                </tr>
            """
        
        ping_html += "</table></div>"
        sections.append(ping_html)
    
    # Section Port Scan
    if 'port_scan' in data and data['port_scan']:
        ports = data['port_scan']
        port_html = f"""
        <div class="section">
            <h2>🔌 Scan de ports ({len(ports)} ports ouverts)</h2>
            <table>
                <tr><th>Port</th><th>Statut</th><th>Service</th></tr>
        """
        
        for port in ports:
            port_html += f"""
                <tr>
                    <td>{port.get('port', 'N/A')}</td>
                    <td><span class="success">{port.get('status', 'N/A')}</span></td>
                    <td>{port.get('service', 'N/A')}</td>
                </tr>
            """
        
        port_html += "</table></div>"
        sections.append(port_html)
    
    # Section Banners
    if 'banners' in data and data['banners']:
        banners = data['banners']
        banner_html = f"""
        <div class="section">
            <h2>📋 Banner Grabbing ({len(banners)} banners collectés)</h2>
        """
        
        for port, banner_info in banners.items():
            banner_html += f"""
            <h3>Port {port} ({banner_info.get('service', 'Unknown')})</h3>
            <div class="code">{banner_info.get('banner', 'N/A')}</div>
            """
        
        banner_html += "</div>"
        sections.append(banner_html)
    
    return sections