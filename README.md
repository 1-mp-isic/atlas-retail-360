# Atlas Retail 360

Plateforme décisionnelle pour le comité de direction d'Atlas Retail.
Projet semestriel · Master 1 SID · 2026–2027 · équipe de 3.

Toutes les données sont synthétiques et produites par le générateur de ce dépôt.
Aucune donnée réelle, aucun identifiant réel.

## État d'avancement

| Phase | Semaines | État |
| --- | --- | --- |
| Fondations : accès, environnements, chaîne MICRO | S1–S2 | en cours |
| Générateur, contrats, ingestion Bronze | S3–S4 | générateur fonctionnel |
| Silver, règles de CA et de marge | S5–S6 | démarré (2 modèles) |
| CDC, incrémental, historisation | S7–S8 | à venir |
| Gold, qualité, publication certifiée | S9–S10 | à venir |
| Power BI et dbt Charts | S11–S12 | à venir |
| Incidents, CI, performance | S13–S14 | à venir |
| Gel, dossier, soutenance | S15–S16 | à venir |

Détail des jalons et des conditions de passage : `docs/plan.md`.

## Ce qui tourne aujourd'hui

- Générateur Python déterministe, profils MICRO et STANDARD, seed de référence 42
- Les 10 cas de recette T01 à T10 avec leurs oracles, écrits indépendamment du SQL
- Manifeste de lots avec checksum SHA-256 par fichier
- 30 contrôles automatisés sur le générateur et les contrats
- Projet dbt : sources déclarées, 2 modèles de préparation, 2 tests métier,
  1 snapshot CRM, 2 macros

## Prérequis

- Python 3.11 ou plus
- Git
- Un compte Databricks Free Edition par étudiant (aucun partage de compte ni de jeton)
- Power BI Desktop, sur un poste Windows, pour la restitution

## Installation

```bash
git clone <url-du-depot>
cd atlas-retail-360
```

Environnement Python, sous Windows (PowerShell) :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".\generator[dev]"
```

Sous Linux ou macOS :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "./generator[dev]"
```

## Générer les données

```bash
# Profil MICRO : les cas de recette, pour développer et vérifier à la main
python -m atlas_gen --seed 42 --profile MICRO --output-dir data/micro

# Profil STANDARD : le jeu complet, pour la recette et la soutenance
python -m atlas_gen --seed 42 --profile STANDARD --output-dir data/standard
```

Volumes produits par STANDARD : 30 000 commandes, 60 000 lignes, 6 000 clients,
1 183 versions produit, 12 magasins, 120 000 mouvements de stock.

Vérifier le déterminisme : générez deux fois dans deux répertoires différents,
puis comparez les champs `checksum` des deux `manifest.json`. Ils doivent être
identiques.

## Lancer les contrôles

```bash
pytest generator/tests -v
sqlfluff lint dbt_project/models
```

## Configurer la connexion Databricks

1. Copiez `dbt_project/profiles.yml.example` vers `~/.dbt/profiles.yml`
   (sous Windows : `%USERPROFILE%\.dbt\profiles.yml`).
2. Relevez `host` et `http_path` dans Databricks, sous
   **SQL Warehouses → votre warehouse → Connection details**.
3. Créez un jeton dans **Settings → Developer → Access tokens**.
4. Exportez les variables d'environnement, sans jamais les committer :

```bash
export DATABRICKS_HOST="adb-xxxx.azuredatabricks.net"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/xxxx"
export DATABRICKS_TOKEN="dapi..."
```

Sous Windows (PowerShell) :

```powershell
$env:DATABRICKS_HOST = "adb-xxxx.azuredatabricks.net"
$env:DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/xxxx"
$env:DATABRICKS_TOKEN = "dapi..."
```

5. Vérifiez :

```bash
cd dbt_project
dbt debug
dbt deps
```

## Exécuter dbt

```bash
cd dbt_project
dbt build --select tag:silver
dbt snapshot
dbt docs generate && dbt docs serve
```

## Organisation du dépôt

```
generator/          Générateur Python et ses tests, indépendant de dbt
  src/atlas_gen/
    contracts.py      Contrats de sources, un seul endroit qui fait foi
    recette.py        Cas T01 à T10 et leurs oracles
    standard.py       Jeu synthétique complet et déterministe
    writers.py        Écriture des lots et manifeste avec checksums
  tests/            Contrôles indépendants des transformations

ingestion/          Chargement Bronze vers Databricks (scripts dédiés, pas dbt)

dbt_project/        Transformations Silver et Gold
  models/staging/     Préparation : états CDC, typage, éligibilité
  models/marts/       Faits, dimensions et agrégats certifiés
  macros/             Conversion EUR, tests génériques métier
  snapshots/          Capture de l'état courant du CRM
  tests/              Assertions métier

docs/               Plan, fiche d'accès, dictionnaire, décisions d'architecture
scripts/            Validation locale et orchestration
```

## Règles de travail

- Aucune correction manuelle dans une table, un fichier ou un rapport.
  Ce qui n'est pas dans un script n'existe pas.
- Les oracles sont écrits avant le SQL correspondant. Recopier la formule de
  production dans un test ne prouve rien.
- Une branche par fonctionnalité, une revue par un membre d'un autre axe
  avant toute fusion.
- Les secrets passent par l'environnement, jamais par Git.

## Équipe

| Axe | Membre | Périmètre |
| --- | --- | --- |
| A — Données et qualité | à compléter | Générateur, anomalies, ingestion, oracles |
| B — Transformation et temporalité | à compléter | dbt, Silver et Gold, CDC, publication |
| C — Restitution et exploitation | à compléter | Power BI, dbt Charts, runbook, CI |
