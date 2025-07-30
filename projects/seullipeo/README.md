# Seullipeo (슬리퍼) - Framework d'Escalade de Privilèges Linux

```
╔══════════════════════════════════════════════════════════════════════════════╗
║     ███████╗███████╗██╗   ██╗██╗     ██╗     ██╗██████╗ ███████╗ ██████╗     ║
║     ██╔════╝██╔════╝██║   ██║██║     ██║     ██║██╔══██╗██╔════╝██╔═══██╗    ║
║     ███████╗█████╗  ██║   ██║██║     ██║     ██║██████╔╝█████╗  ██║   ██║    ║
║     ╚════██║██╔══╝  ██║   ██║██║     ██║     ██║██╔═══╝ ██╔══╝  ██║   ██║    ║
║     ███████║███████╗╚██████╔╝███████╗███████╗██║██║     ███████╗╚██████╔╝    ║
║     ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝╚═╝     ╚══════╝ ╚═════╝     ║
║                           슬리퍼 (Sleeper)                                    ║
║                    Linux Privilege Escalation Framework                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 📖 Description

**Seullipeo** (슬리퍼, "Sleeper" en coréen) est un framework d'escalade de privilèges Linux développé à des fins éducatives et de test de pénétration autorisé. Il automatise la détection et l'exploitation des vulnérabilités courantes permettant l'élévation de privilèges sur les systèmes Unix/Linux.

### 🎯 Objectifs

- **Éducation** : Comprendre les mécanismes d'escalade de privilèges
- **Tests de sécurité** : Évaluer la sécurité des systèmes Linux
- **Automatisation** : Simplifier les audits de sécurité
- **Modularité** : Framework extensible pour nouveaux exploits

## 🚀 Fonctionnalités

### 📋 Modules d'Exploitation

| Module | Description | Niveau de Risque |
|--------|-------------|------------------|
| **CRON** | Détection et exploitation des tâches cron vulnérables | Medium |
| **SUID** | Analyse des binaires SUID exploitables | High |
| **PASSWD WRITABLE** | Exploitation des fichiers système modifiables | Critical |
| **SUDO VERSION** | Exploitation des vulnérabilités sudo | High |
| **WORLD WRITABLE** | Recherche de fichiers modifiables par tous | Medium |

### 🎛️ Interfaces

- **CLI** : Interface en ligne de commande avec arguments
- **Shell interactif** : REPL style Metasploit avec commandes dynamiques
- **Export** : Sauvegarde des résultats en JSON et texte

### ⚡ Modes d'Exécution

- **Scan** : Détection uniquement (pas d'exploitation)
- **Exploit** : Exploitation directe des vulnérabilités
- **Agressif** : Scan + exploitation automatique

## 📁 Structure du Projet

```
seullipeo/
├── main.py                      # Point d'entrée principal
├── cli/
│   └── cli.py                   # Interface CLI (argparse)
├── shell/
│   └── shell.py                 # Interface REPL interactive
├── exploits/
│   ├── __init__.py              # Gestionnaire des modules
│   ├── cron.py                  # Module exploitation cron
│   ├── suid.py                  # Module binaires SUID
│   ├── passwd_writable.py       # Module /etc/passwd modifiable
│   └── ...                      # Autres modules
├── utils/
│   ├── display.py               # Utilitaires d'affichage
│   ├── system.py                # Fonctions système
│   └── logger.py                # Système de logging
├── output/                      # Résultats d'exploitation
├── logs/                        # Fichiers de log
├── sessions/                    # Sessions sauvegardées
└── requirements.txt             # Dépendances (aucune!)
```

## 🛠️ Installation

### Prérequis
- Python 3.6+
- Système Linux/Unix
- Aucune dépendance externe requise !

### Installation Simple

```bash
# Cloner le repository
git clone https://github.com/huosh1/seullipeo.git
cd seullipeo

# Rendre exécutable
chmod +x main.py

# Test rapide
python3 main.py --help
```

### Installation Développeur

```bash
# Clone + environnement virtuel
git clone https://github.com/huosh1/seullipeo.git
cd seullipeo
python3 -m venv venv
source venv/bin/activate

# Dépendances développement (optionnel)
pip install pytest black pylint coverage
```

## 📚 Utilisation

### Mode CLI (Ligne de Commande)

```bash
# Scan uniquement avec module SUID
python3 main.py --scan --suid

# Exploitation directe des tâches cron
python3 main.py --exploit --cron --output results.txt

# Mode agressif (scan + exploit) tous modules
python3 main.py --aggressive --all-modules --json report.json

# Modules spécifiques
python3 main.py --scan --cron --suid --passwd --output scan.txt

# Aide détaillée
python3 main.py --help
```

### Mode Shell Interactif

```bash
# Lancement du shell
python3 main.py --shell
```

**Commandes shell principales :**

```bash
# Navigation
seullipeo> help                    # Aide
seullipeo> list                    # Liste des modules
seullipeo> use cron                # Charger module cron

# Dans un module
seullipeo[cron]> info              # Infos du module
seullipeo[cron]> scan              # Lancer scan
seullipeo[cron]> list vulns        # Lister vulnérabilités
seullipeo[cron]> exploit all       # Exploiter tout
seullipeo[cron]> exploit 1         # Exploiter vulnérabilité #1
seullipeo[cron]> back              # Retour shell principal

# Utilitaires
seullipeo> set LHOST 192.168.1.100 # Définir variables
seullipeo> show options            # Voir variables
seullipeo> save-session test       # Sauvegarder session
seullipeo> history                 # Historique commandes
```

### Options CLI Complètes

```bash
# Modules
--cron                  # Module tâches cron
--suid                  # Module binaires SUID  
--passwd                # Module /etc/passwd modifiable
--all-modules           # Tous les modules

# Modes d'exécution
--scan                  # Scan uniquement
--exploit               # Exploitation directe
--aggressive            # Scan + exploit automatique

# Sortie
--output FILE           # Fichier texte
--json FILE             # Fichier JSON
--verbose               # Mode verbeux

# Utilitaires
--list-modules          # Liste modules disponibles
--shell                 # Lance shell interactif
--banner                # Affiche bannière
--help                  # Aide
```

## 🔍 Exemples d'Utilisation

### Audit de Sécurité Rapide

```bash
# Scan complet tous modules
python3 main.py --scan --all-modules --json audit.json

# Analyse des résultats
cat audit.json | jq '.summary'
```

### Test d'Escalade Complète

```bash
# Mode agressif avec sauvegarde
python3 main.py --aggressive --cron --suid --passwd \
  --output escalation.txt --json escalation.json
```

### Session Interactive

```bash
python3 main.py --shell
seullipeo> use suid
seullipeo[suid]> scan
seullipeo[suid]> list vulns
seullipeo[suid]> exploit 1
seullipeo[suid]> notes "Binaire find exploitable"
seullipeo[suid]> save suid_results.json
seullipeo[suid]> back
seullipeo> save-session audit_20250131
```

## 🧪 Modules Détaillés

### Module CRON

Détecte et exploite :
- Crontabs système modifiables (`/etc/crontab`)
- Répertoires cron modifiables (`/etc/cron.d/`, `/etc/cron.daily/`)
- Scripts cron avec permissions incorrectes
- Tâches cron exécutées avec privilèges élevés

```bash
seullipeo[cron]> set LHOST 192.168.1.100
seullipeo[cron]> set LPORT 4444
seullipeo[cron]> scan
seullipeo[cron]> exploit all
```

### Module SUID

Analyse les binaires SUID exploitables :
- Binaires connus : `find`, `vim`, `python`, `bash`, etc.
- Détection automatique des chemins d'exploitation
- Support de 20+ binaires exploitables
- Génération de payloads adaptés

```bash
seullipeo[suid]> scan
# Détecte: /usr/bin/find (SUID root)
seullipeo[suid]> exploit 1
# Exécute: find /etc/passwd -exec whoami \;
```

### Module PASSWD WRITABLE

Exploite les fichiers système modifiables :
- `/etc/passwd` modifiable → création utilisateur root
- `/etc/shadow` modifiable → modification mots de passe
- `/etc/group` modifiable → ajout groupes privilégiés
- Backup automatique des fichiers originaux

```bash
seullipeo[passwd]> set USERNAME hacker
seullipeo[passwd]> set PASSWORD toor123
seullipeo[passwd]> scan
seullipeo[passwd]> exploit 1
# Crée utilisateur UID 0 avec mot de passe
```

## 📊 Format des Résultats

### Export JSON

```json
{
  "timestamp": "2025-01-31T10:30:00",
  "version": "1.0.0",
  "modules": {
    "suid": {
      "scan_results": [
        {
          "type": "exploitable_suid",
          "path": "/usr/bin/find",
          "binary_name": "find",
          "risk": "High",
          "description": "Binaire SUID exploitable: /usr/bin/find"
        }
      ],
      "exploit_results": [
        {
          "success": true,
          "description": "find SUID exploité",
          "exploit_cmd": "find /etc/passwd -exec whoami \\;"
        }
      ]
    }
  },
  "summary": {
    "total_vulns": 1,
    "exploited": 1,
    "failed": 0
  }
}
```

### Export Texte

```
==============================================================
SEULLIPEO - RAPPORT D'ESCALADE DE PRIVILÈGES
==============================================================
Timestamp: 2025-01-31T10:30:00
Version: 1.0.0

RÉSUMÉ:
--------------------
Vulnérabilités trouvées: 1
Exploits réussis: 1
Exploits échoués: 0

MODULE: SUID
------------------------------
Vulnérabilités détectées:
  1. Binaire SUID exploitable: /usr/bin/find
     Chemin: /usr/bin/find

Résultats d'exploitation:
  - SUCCÈS: find SUID exploité
```

## 🛡️ Sécurité et Éthique

### ⚠️ Avertissements Importants

**Seullipeo doit être utilisé UNIQUEMENT sur :**
- ✅ Vos propres systèmes
- ✅ Systèmes avec autorisation écrite explicite
- ✅ Environnements de test/lab dédiés
- ✅ CTF et challenges autorisés

**Usage INTERDIT sur :**
- ❌ Systèmes sans autorisation
- ❌ Infrastructure de production sans accord
- ❌ Systèmes tiers ou compromis

### 🔒 Bonnes Pratiques

1. **Tests isolés** : Utilisez des VMs ou containers
2. **Backups** : Seullipeo crée des backups automatiques
3. **Logs** : Toutes les actions sont loggées
4. **Nettoyage** : Supprimez les artéfacts après tests
5. **Documentation** : Documentez vos tests de sécurité

### ⚖️ Responsabilité Légale

L'auteur et les contributeurs de Seullipeo **déclinent toute responsabilité** en cas d'usage malveillant, illégal ou non autorisé. L'utilisateur est entièrement responsable de l'usage qu'il fait de cet outil.



