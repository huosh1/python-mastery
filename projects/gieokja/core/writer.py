"""
Module de génération des write-ups en Markdown
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import configparser

from utils.logger import get_logger
from utils.helpers import truncate_output, format_duration


class WriteupWriter:
    """Classe pour générer les write-ups en Markdown"""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.logger = get_logger()
        self.config = self._load_config()
        
        # Chemins
        self.output_dir = Path(self.config.get('output', 'output_directory', fallback='data'))
        self.template_path = Path(self.config.get('output', 'markdown_template', fallback='templates/writeup.md.tpl'))
        self.output_path = self.output_dir / f"{session_name}.md"
        
        # Créer le répertoire de sortie
        self.output_dir.mkdir(exist_ok=True)
        
        # Sections du write-up
        self.sections = self._parse_sections()
        self.content_buffer = {section: [] for section in self.sections}
        
        # Template
        self.template = self._load_template()
    
    def _load_config(self):
        """Charger la configuration"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config
    
    def _parse_sections(self):
        """Parser les sections depuis la configuration"""
        sections_str = self.config.get('output', 'sections', 
            fallback='Informations générales, Reconnaissance, Énumération Web, Accès initial, Escalade de privilèges, Post-exploitation, Flags trouvés, Notes et observations')
        return [s.strip() for s in sections_str.split(',')]
    
    def _load_template(self):
        """Charger le template Markdown"""
        if self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')
        else:
            # Template par défaut
            return """# 📝 Write-up: {session_name}

**Date**: {date}  
**Auteur**: {author}  
**Machine cible**: {target}  
**Durée**: {duration}

---

## 📊 Résumé exécutif

{summary}

---

{content}

---

## 📈 Statistiques

- **Commandes exécutées**: {total_commands}
- **Flags trouvés**: {total_flags}
- **Notes prises**: {total_notes}

---

*Généré automatiquement par Gieokja - The Rememberer*
"""
    
    def write_session_data(self, session_data: Dict[str, Any]):
        """Écrire les données de session dans le write-up"""
        # Réinitialiser le buffer de contenu
        self.content_buffer = {section: [] for section in self.sections}
        
        # Organiser les commandes par catégorie
        self._organize_commands(session_data['commands'])
        
        # Ajouter les flags
        self._add_flags_section(session_data['flags'])
        
        # Ajouter les notes
        self._add_notes_section(session_data['notes'])
        
        # Ajouter les TODOs
        self._add_todos_section(session_data['todos'])
        
        # Générer le contenu final
        content = self._generate_content()
        
        # Calculer les statistiques
        stats = self._calculate_statistics(session_data)
        
        # Remplacer les placeholders dans le template
        output = self.template.format(
            session_name=self.session_name,
            date=datetime.now().strftime("%d/%m/%Y %H:%M"),
            author=session_data.get('current_user', 'Unknown'),
            target=session_data.get('target_ip', 'Unknown'),
            duration=format_duration(
                datetime.now() - session_data['start_time']
            ),
            summary=self._generate_summary(session_data),
            content=content,
            total_commands=stats['total_commands'],
            total_flags=stats['total_flags'],
            total_notes=stats['total_notes']
        )
        
        # Écrire le fichier
        self.output_path.write_text(output, encoding='utf-8')
        self.logger.info(f"Write-up sauvegardé: {self.output_path}")
    
    def _organize_commands(self, commands: List[Dict[str, Any]]):
        """Organiser les commandes par section"""
        for entry in commands:
            category = entry.get('category', 'Général')
            section = self._category_to_section(category)
            
            # Formater l'entrée de commande
            formatted_entry = self._format_command_entry(entry)
            
            if section in self.content_buffer:
                self.content_buffer[section].append(formatted_entry)
    
    def _category_to_section(self, category: str) -> str:
        """Mapper une catégorie à une section du write-up"""
        mapping = {
            'Reconnaissance': 'Reconnaissance',
            'Web Enumeration': 'Énumération Web',
            'Exploitation': 'Accès initial',
            'Privilege Escalation': 'Escalade de privilèges',
            'Post Exploitation': 'Post-exploitation',
            'Général': 'Notes et observations'
        }
        return mapping.get(category, 'Notes et observations')
    
    def _format_command_entry(self, entry: Dict[str, Any]) -> str:
        """Formater une entrée de commande"""
        timestamp = entry['timestamp'].strftime("%H:%M:%S")
        command = entry['command']
        output = entry.get('output', '')
        important = entry.get('important', False)
        
        # Marquer les commandes importantes
        marker = "⭐ " if important else ""
        
        # Construire l'entrée
        result = f"\n### {marker}[{timestamp}] {command}\n\n"
        
        if output:
            # Limiter la taille de la sortie
            max_lines = self.config.getint('general', 'max_command_output_lines', fallback=100)
            truncated_output = truncate_output(output, max_lines)
            
            # Ajouter la sortie dans un bloc de code
            result += f"```\n{truncated_output}\n```\n"
        
        return result
    
    def _add_flags_section(self, flags: List[Dict[str, Any]]):
        """Ajouter la section des flags"""
        if not flags:
            return
        
        content = []
        for i, flag_entry in enumerate(flags, 1):
            flag = flag_entry['flag']
            timestamp = flag_entry['timestamp'].strftime("%H:%M:%S")
            command = flag_entry.get('command', 'N/A')
            auto = " (auto-détecté)" if flag_entry.get('auto_detected') else ""
            
            content.append(f"{i}. **`{flag}`** - Trouvé à {timestamp}{auto}")
            if command and command != 'N/A':
                content.append(f"   - Commande: `{command}`")
        
        self.content_buffer['Flags trouvés'] = content
    
    def _add_notes_section(self, notes: List[Dict[str, Any]]):
        """Ajouter la section des notes"""
        if not notes:
            return
        
        content = []
        for note_entry in notes:
            note = note_entry['note']
            timestamp = note_entry['timestamp'].strftime("%H:%M:%S")
            related_cmd = note_entry.get('related_command', '')
            
            content.append(f"- **[{timestamp}]** {note}")
            if related_cmd:
                content.append(f"  - Contexte: `{related_cmd[:60]}...`")
        
        if content:
            self.content_buffer['Notes et observations'].extend(["\n#### 📝 Notes\n"] + content)
    
    def _add_todos_section(self, todos: List[Dict[str, Any]]):
        """Ajouter la section des TODOs"""
        if not todos:
            return
        
        content = ["\n#### 📋 TODOs\n"]
        for todo_entry in todos:
            todo = todo_entry['todo']
            completed = "✓" if todo_entry.get('completed') else "○"
            timestamp = todo_entry['timestamp'].strftime("%H:%M:%S")
            
            content.append(f"- [{completed}] {todo} *(ajouté à {timestamp})*")
        
        if len(content) > 1:
            self.content_buffer['Notes et observations'].extend(content)
    
    def _generate_content(self) -> str:
        """Générer le contenu complet du write-up"""
        sections_content = []
        
        for section in self.sections:
            if self.content_buffer[section]:
                # Ajouter le titre de section
                sections_content.append(f"## {self._get_section_icon(section)} {section}\n")
                
                # Ajouter le contenu
                if isinstance(self.content_buffer[section], list):
                    sections_content.extend(self.content_buffer[section])
                else:
                    sections_content.append(self.content_buffer[section])
                
                sections_content.append("\n")
        
        return '\n'.join(sections_content)
    
    def _get_section_icon(self, section: str) -> str:
        """Obtenir l'icône pour une section"""
        icons = {
            'Informations générales': '📋',
            'Reconnaissance': '🔍',
            'Énumération Web': '🌐',
            'Accès initial': '🚪',
            'Escalade de privilèges': '⬆️',
            'Post-exploitation': '💎',
            'Flags trouvés': '🏁',
            'Notes et observations': '📝'
        }
        return icons.get(section, '•')
    
    def _generate_summary(self, session_data: Dict[str, Any]) -> str:
        """Générer un résumé exécutif"""
        flags_count = len(session_data['flags'])
        target = session_data.get('target_ip', 'Unknown')
        
        summary_parts = []
        
        if target != 'Unknown':
            summary_parts.append(f"Machine cible: **{target}**")
        
        if flags_count > 0:
            summary_parts.append(f"**{flags_count} flag(s)** trouvé(s)")
        
        # Analyser les commandes pour déterminer les techniques utilisées
        commands = session_data['commands']
        techniques = set()
        
        for cmd in commands:
            cmd_str = cmd['command'].lower()
            if 'nmap' in cmd_str:
                techniques.add("scan de ports")
            elif any(tool in cmd_str for tool in ['gobuster', 'dirbuster', 'ffuf']):
                techniques.add("énumération web")
            elif any(tool in cmd_str for tool in ['sqlmap', 'burp']):
                techniques.add("tests d'injection")
            elif 'msfconsole' in cmd_str or 'exploit' in cmd_str:
                techniques.add("exploitation")
            elif any(priv in cmd_str for priv in ['sudo -l', 'linpeas', 'pspy']):
                techniques.add("élévation de privilèges")
        
        if techniques:
            summary_parts.append(f"Techniques utilisées: {', '.join(techniques)}")
        
        return ' | '.join(summary_parts) if summary_parts else "Session de reconnaissance et d'exploitation CTF"
    
    def _calculate_statistics(self, session_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculer les statistiques de la session"""
        return {
            'total_commands': len(session_data['commands']),
            'total_flags': len(session_data['flags']),
            'total_notes': len(session_data['notes']) + len(session_data['todos'])
        }
    
    def finalize(self):
        """Finaliser le write-up"""
        self.logger.info("Finalisation du write-up")
        # La sauvegarde finale sera gérée par le tracker
    
    def export(self, format='md'):
        """Exporter le write-up dans différents formats"""
        if format == 'md':
            return self.output_path
        elif format == 'html':
            # TODO: Implémenter l'export HTML
            pass
        elif format == 'pdf':
            # TODO: Implémenter l'export PDF
            pass
        
        return self.output_path