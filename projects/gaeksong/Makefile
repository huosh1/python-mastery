# Makefile pour Gaeksong
# Outil de reconnaissance active et passive

.PHONY: help install test clean lint format docs run-passive run-active

# Variables
PYTHON = python3
PIP = pip3
VENV = venv
REQUIREMENTS = requirements.txt
MAIN_SCRIPT = gaeksong.py

# Couleurs pour l'affichage
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)Gaeksong - Makefile$(NC)"
	@echo "$(GREEN)Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Installe les dépendances
	@echo "$(GREEN)Installation des dépendances...$(NC)"
	$(PIP) install -r $(REQUIREMENTS)
	@echo "$(GREEN)✓ Installation terminée$(NC)"

install-dev: ## Installe les dépendances de développement
	@echo "$(GREEN)Installation des dépendances de développement...$(NC)"
	$(PIP) install -r $(REQUIREMENTS)
	$(PIP) install pylint black flake8 pytest coverage
	@echo "$(GREEN)✓ Installation dev terminée$(NC)"

venv: ## Crée un environnement virtuel
	@echo "$(GREEN)Création de l'environnement virtuel...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(YELLOW)Activez l'environnement avec: source $(VENV)/bin/activate$(NC)"

test: ## Lance les tests
	@echo "$(GREEN)Lancement des tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)✓ Tests terminés$(NC)"

test-coverage: ## Lance les tests avec couverture
	@echo "$(GREEN)Lancement des tests avec couverture...$(NC)"
	$(PYTHON) -m coverage run -m pytest tests/
	$(PYTHON) -m coverage report
	$(PYTHON) -m coverage html
	@echo "$(GREEN)✓ Rapport de couverture généré dans htmlcov/$(NC)"

lint: ## Vérifie le code avec pylint
	@echo "$(GREEN)Vérification du code avec pylint...$(NC)"
	$(PYTHON) -m pylint $(MAIN_SCRIPT) modules/
	@echo "$(GREEN)✓ Lint terminé$(NC)"

format: ## Formate le code avec black
	@echo "$(GREEN)Formatage du code avec black...$(NC)"
	$(PYTHON) -m black $(MAIN_SCRIPT) modules/
	@echo "$(GREEN)✓ Code formaté$(NC)"

flake8: ## Vérifie le style avec flake8
	@echo "$(GREEN)Vérification du style avec flake8...$(NC)"
	$(PYTHON) -m flake8 $(MAIN_SCRIPT) modules/
	@echo "$(GREEN)✓ Style vérifié$(NC)"

clean: ## Nettoie les fichiers temporaires
	@echo "$(GREEN)Nettoyage des fichiers temporaires...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

docs: ## Génère la documentation
	@echo "$(GREEN)Génération de la documentation...$(NC)"
	mkdir -p docs/
	$(PYTHON) -c "import modules; help(modules)" > docs/modules.txt
	@echo "$(GREEN)✓ Documentation générée dans docs/$(NC)"

build: ## Construit le package
	@echo "$(GREEN)Construction du package...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)✓ Package construit dans dist/$(NC)"

install-package: build ## Installe le package localement
	@echo "$(GREEN)Installation du package...$(NC)"
	$(PIP) install dist/*.whl --force-reinstall
	@echo "$(GREEN)✓ Package installé$(NC)"

# Commandes de test rapide
run-passive: ## Test reconnaissance passive sur google.com
	@echo "$(GREEN)Test reconnaissance passive...$(NC)"
	$(PYTHON) $(MAIN_SCRIPT) passive --domain google.com --dns --output results/test_passive.json

run-active: ## Test reconnaissance active sur localhost
	@echo "$(GREEN)Test reconnaissance active...$(NC)"
	$(PYTHON) $(MAIN_SCRIPT) active --target 127.0.0.1 --ports 22,80,443 --output results/test_active.json

demo: ## Démonstration complète
	@echo "$(GREEN)Démonstration de Gaeksong...$(NC)"
	@echo "$(YELLOW)1. Test reconnaissance passive...$(NC)"
	$(PYTHON) $(MAIN_SCRIPT) passive --domain example.com --dns
	@echo "$(YELLOW)2. Test reconnaissance active...$(NC)"
	$(PYTHON) $(MAIN_SCRIPT) active --target 127.0.0.1 --ports 80,443
	@echo "$(GREEN)✓ Démonstration terminée$(NC)"

# Validation complète avant commit
validate: lint flake8 test ## Validation complète du code
	@echo "$(GREEN)✓ Validation complète réussie$(NC)"

# Installation complète pour développement
setup-dev: venv install-dev ## Configuration complète pour développement
	@echo "$(GREEN)✓ Environnement de développement prêt$(NC)"
	@echo "$(YELLOW)N'oubliez pas d'activer l'environnement virtuel:$(NC)"
	@echo "$(BLUE)source $(VENV)/bin/activate$(NC)"

# Commandes de déploiement
check-security: ## Vérifie les vulnérabilités de sécurité
	@echo "$(GREEN)Vérification de sécurité...$(NC)"
	$(PIP) install safety
	safety check
	@echo "$(GREEN)✓ Vérification de sécurité terminée$(NC)"

update-deps: ## Met à jour les dépendances
	@echo "$(GREEN)Mise à jour des dépendances...$(NC)"
	$(PIP) list --outdated
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	@echo "$(GREEN)✓ Dépendances mises à jour$(NC)"

# Création de la structure de répertoires
create-dirs: ## Crée la structure de répertoires
	@echo "$(GREEN)Création de la structure de répertoires...$(NC)"
	mkdir -p results/
	mkdir -p logs/
	mkdir -p tests/
	mkdir -p docs/
	mkdir -p templates/
	@echo "$(GREEN)✓ Structure créée$(NC)"

# Informations système
info: ## Affiche les informations système
	@echo "$(BLUE)=== Informations Système ===$(NC)"
	@echo "$(YELLOW)Python:$(NC) $$($(PYTHON) --version)"
	@echo "$(YELLOW)Pip:$(NC) $$($(PIP) --version)"
	@echo "$(YELLOW)OS:$(NC) $$(uname -s)"
	@echo "$(YELLOW)Architecture:$(NC) $$(uname -m)"
	@echo "$(YELLOW)Répertoire:$(NC) $$(pwd)"

# Raccourcis
i: install ## Raccourci pour install
t: test ## Raccourci pour test
c: clean ## Raccourci pour clean
l: lint ## Raccourci pour lint
f: format ## Raccourci pour format

# Installation en une commande
all: create-dirs install test ## Installation complète et tests