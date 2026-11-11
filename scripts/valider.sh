#!/usr/bin/env bash
# Validation locale, à lancer avant toute pull request.
# Les contrôles statiques (1 à 3) ne nécessitent aucune connexion.
# Les contrôles connectés (4 et 5) exigent Databricks : ce ne sont PAS
# des tests hors connexion, et le rapport doit maintenir la distinction.

set -euo pipefail

echo "== 1. Aucun secret dans l'index Git =="
if git diff --cached --name-only | grep -Ex 'profiles\.yml|\.env'; then
  echo "ECHEC : un fichier de secrets est sur le point d'être committé."
  exit 1
fi
echo "OK"

echo "== 2. Tests du générateur =="
pytest generator/tests -q

echo "== 3. Lint SQL =="
sqlfluff lint dbt_project/models || true

echo "== 4. Compilation dbt (connexion requise) =="
cd dbt_project
dbt parse

echo "== 5. Construction ciblée et tests (connexion requise) =="
dbt build --select tag:silver

echo
echo "Validation locale terminée."
