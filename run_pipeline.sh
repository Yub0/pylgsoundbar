#!/bin/bash
# Script pour exécuter la pipeline complète de qualité de code et tests

set -e  # Arrête le script en cas d'erreur

echo "🔄 Exécution de la pipeline de tests et d'analyse de code..."

echo -e "\n🧹 Formatage du code avec Black..."
poetry run black --check src tests
if [ $? -eq 0 ]; then
    echo "✅ Le code est bien formaté."
else
    echo "❌ Le formatage du code a échoué. Exécutez 'poetry run black src tests' pour formater le code."
    exit 1
fi

echo -e "\n🔍 Vérification du code avec Flake8..."
poetry run flake8 src tests
if [ $? -eq 0 ]; then
    echo "✅ Aucun problème détecté par Flake8."
else
    echo "❌ Flake8 a détecté des problèmes. Veuillez les corriger."
    exit 1
fi

echo -e "\n🔍 Vérification du code avec Pylint..."
poetry run pylint src/lgsoundbar
if [ $? -eq 0 ]; then
    echo "✅ Aucun problème détecté par Pylint."
else
    echo "❌ Pylint a détecté des problèmes. Veuillez les corriger."
    exit 1
fi

echo -e "\n🧪 Exécution des tests avec Pytest..."
poetry run pytest
if [ $? -eq 0 ]; then
    echo "✅ Tous les tests sont passés."
else
    echo "❌ Certains tests ont échoué. Veuillez les corriger."
    exit 1
fi

echo -e "\n✅ La pipeline complète a été exécutée avec succès! ✨"