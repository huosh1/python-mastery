# Gaeksong - Outil de Reconnaissance Active et Passive

## Description

Gaeksong est un outil de reconnaissance en cybersécurité développé en Python, permettant d'effectuer des reconnaissances actives et passives sur des cibles réseau. Il est conçu à des fins éducatives et de test de sécurité autorisé uniquement.

## Fonctionnalités

### Reconnaissance Passive
- **WHOIS Lookup** : Récupération des informations d'enregistrement de domaine
- **DNS Lookup** : Résolution des enregistrements DNS (A, AAAA, MX, NS, TXT, CNAME, SOA)
- **Bruteforce de sous-domaines** : Découverte de sous-domaines via wordlist

### Reconnaissance Active
- **Ping Sweep** : Détection d'hôtes actifs sur une plage réseau
- **Port Scan** : Scan de ports TCP sur une cible
- **Banner Grabbing** : Récupération des bannières de services

### Export et Reporting
- Export des résultats en format JSON
- Export des résultats en format HTML (rapport visuel)
- Logging détaillé des opérations

## Structure du Projet

```
gaeksong/
├── gaeksong.py              # Point d'entrée principal
├── modules/
│   ├── __init__.py         # Initialisation du package
│   ├── passive.py          # Module reconnaissance passive
│   ├── active.py           # Module reconnaissance active
│   ├── export.py           # Module d'export
│   └── utils.py            # Utilitaires
├── wordlists/
│   └── subdomains.txt      # Liste de sous-domaines
├── results/                # Répertoire des résultats (créé automatiquement)
├── requirements.txt        # Dépendances Python
└── README.md              # Documentation
```

## Installation

1. Cloner le repository
```bash
git clone https://github.com/votre-username/gaeksong.git
cd gaeksong
```

2. Installer les dépendances
```bash
pip install -r requirements.txt
```

3. Rendre le script exécutable (Linux/Mac)
```bash
chmod +x gaeksong.py
```

## Utilisation

### Reconnaissance Passive

```bash
# WHOIS et DNS lookup
python3 gaeksong.py passive --domain example.com --whois --dns

# Bruteforce de sous-domaines
python3 gaeksong.py passive --domain example.com --dns-brute wordlists/subdomains.txt

# Reconnaissance complète avec export
python3 gaeksong.py passive --domain example.com --whois --dns --dns-brute wordlists/subdomains.txt --output results/example.json
```

### Reconnaissance Active

```bash
# Scan de ports spécifiques
python3 gaeksong.py active --target 192.168.1.1 --ports 22,80,443

# Ping sweep sur une plage réseau
python3 gaeksong.py active --ping-sweep 192.168.1.0/24

# Scan complet avec banner grabbing
python3 gaeksong.py active --target 10.10.10.5 --ports 22,80,443,8080 --banner --output results/scan.json
```

### Options Disponibles

#### Commande `passive`
- `--domain` : Domaine cible (requis)
- `--whois` : Active le lookup WHOIS
- `--dns` : Active le lookup DNS
- `--dns-brute` : Lance le bruteforce avec une wordlist
- `--output` : Fichier de sortie JSON

#### Commande `active`
- `--target` : Adresse IP cible (requis)
- `--ports` : Liste de ports séparés par des virgules
- `--ping-sweep` : Plage réseau pour ping sweep (CIDR)
- `--banner` : Active le banner grabbing
- `--output` : Fichier de sortie JSON

## Exemples d'Utilisation

### Reconnaissance d'un domaine complet
```bash
python3 gaeksong.py passive --domain target.com --whois --dns --dns-brute wordlists/subdomains.txt --output results/target_recon.json
```

### Scan réseau interne
```bash
python3 gaeksong.py active --ping-sweep 192.168.1.0/24 --output results/network_sweep.json
```

### Analyse de sécurité d'un serveur
```bash
python3 gaeksong.py active --target 10.10.10.100 --ports 21,22,23,25,53,80,110,443,993,995 --banner --output results/server_analysis.json
```

## Sécurité et Éthique

⚠️ **IMPORTANT** : Cet outil doit être utilisé uniquement sur :
- Vos propres systèmes
- Des systèmes pour lesquels vous avez une autorisation écrite explicite
- Des environnements de test dédiés

L'utilisation non autorisée de cet outil peut être illégale.