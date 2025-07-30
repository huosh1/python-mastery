# ---------------------------------------
# ✅ PASSIVE RECONNAISSANCE CHECKLIST
# ---------------------------------------

# 1. WHOIS lookup
#    - Récupérer les informations d'enregistrement du domaine
#    - Extraire : registrar, dates, noms de serveurs DNS, mails, etc.

# 2. DNS records lookup
#    - Enregistrements A (IPv4)
#    - Enregistrements AAAA (IPv6)
#    - Enregistrements MX (mail)
#    - Enregistrements NS (serveurs DNS)
#    - Enregistrements TXT (SPF, DKIM, Google, etc.)

# 3. Subdomain brute-force
#    - Utiliser une wordlist pour tester des sous-domaines communs
#    - Résoudre chaque sous-domaine vers son IP
#    - Retourner seulement ceux qui existent

# 4. PTR record (reverse DNS)
#    - Faire un reverse DNS de l'adresfrom modules.export import export_to_filese IP pour voir s'il y a un nom associé

# 5. DNS zone transfer test (AXFR)
#    - Tenter un transfert de zone avec chaque serveur NS
#    - Peut révéler **tous les enregistrements DNS** si mal configuré

# 6. SSL/TLS certificate scraping (si le domaine supporte HTTPS)
#    - Récupérer le certificat SSL
#    - Extraire le Common Name (CN), Subject Alternative Names (SAN), date de validité

# 7. Public ASN & IP info
#    - Résoudre l'IP publique du domaine
#    - Chercher à quel AS (Autonomous System) elle appartient
#    - Fournisseur, plage IP, etc. (via whois IP)

# 8. Google dorking (optionnel, non via API)
#    - Générer des requêtes Google dorking (ex: `site:example.com filetype:pdf`)
#    - Afficher des suggestions sans faire de requête directe

# 9. Social media discovery (optionnel)
#    - Rechercher si le domaine est lié à des comptes publics Twitter / LinkedIn / GitHub

# 10. Search engine scraping (optionnel si API)
#     - Résultats passifs via API (ex: `https://crt.sh/`, `shodan`, etc.)

# ---------------------------------------

from modules.export import export_to_file

def whois(domaine)