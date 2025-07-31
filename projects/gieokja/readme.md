# Gieokja (기억자) 

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey.svg)

</div>

---

## À propos

Gieokja est un outil de documentation automatique conçu pour les pentesters et les joueurs CTF. Il capture, organise et génère automatiquement des write-ups détaillés de vos sessions de hacking, vous permettant de vous concentrer sur la résolution des challenges plutôt que sur la prise de notes.

### ✨ Caractéristiques principales

- 🔄 **Tracking automatique** des commandes et de leurs sorties
- 🏁 **Détection intelligente** des flags (THM{}, HTB{}, etc.)
- 📝 **Génération automatique** de write-ups en Markdown
- 🎯 **Catégorisation** des commandes (recon, exploitation, privesc, etc.)
- 💡 **Système de notes** et TODOs intégré
- 🔍 **Hooks personnalisables** pour des actions automatiques
- 📊 **Statistiques détaillées** de vos sessions

## 📦 Installation

### Prérequis

- Python 3.7 ou supérieur
- Linux 
- Terminal avec support des couleurs ANSI

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/huosh1/gieokja.git
cd gieokja

# Installer les dépendances
pip install -r requirements.txt

# Rendre le script exécutable
chmod +x gieokja.py

# (Optionnel) Ajouter au PATH
sudo ln -s $(pwd)/gieokja.py /usr/local/bin/gieokja
```

### Commandes principales

Commandes Gieokja (taper directement dans le terminal):
  gieokja-note <texte> - Ajouter une note
  gieokja-flag [texte] - Marquer un flag
  gieokja-todo <texte> - Ajouter un TODO
  gieokja-save - Forcer la sauvegarde
  gieokja-status - Voir le statut
  gieokja-stop - Arrêter Gieokja



## 🔧 Configuration

Le fichier `config.ini` permet de personnaliser le comportement de Gieokja :

```ini
[tracking]
# Patterns de flags à détecter
flag_patterns = THM{.*?}, HTB{.*?}, flag{.*?}, FLAG{.*?}

# Commandes importantes à mettre en évidence
important_commands = nmap, gobuster, sqlmap, msfconsole

[output]
# Répertoire de sortie des write-ups
output_directory = data

# Nombre maximum de lignes de sortie par commande
max_command_output_lines = 100
```

```


