# 001 — Séparation entre ingestion et dbt

Statut : acceptée · Date : S1

## Contexte

dbt transforme des données déjà chargées dans l'entrepôt. Il ne lit pas de
fichiers plats et ne sait pas appeler une API source. Il faut donc décider où
s'arrête le chargement et où commence la transformation.

## Alternatives

1. **Tout dans dbt**, en lisant les fichiers via des tables externes.
   Rend la couche Bronze implicite, rend les métadonnées de lot difficiles à
   conserver, et mélange deux responsabilités.
2. **Ingestion en Python, transformation en dbt.** Deux outils, deux
   responsabilités, au prix d'une étape supplémentaire à orchestrer.
3. **Ingestion via un outil tiers** (Fivetran, Airbyte). Hors socle gratuit et
   non exigé par l'énoncé.

## Choix

Alternative 2. Les scripts de `ingestion/` chargent les fichiers du générateur
en tables Delta Bronze, en conservant le payload d'origine, `file_name`,
`row_number`, `record_hash` et les métadonnées de lot. dbt part de ces tables,
déclarées comme sources.

## Conséquences

- La couche Bronze est une vraie couche, pas un effet de bord.
- Le rejeu d'un lot est une opération d'ingestion, testable isolément.
- Une étape d'orchestration supplémentaire à décrire dans le runbook.
- Python ne doit pas servir à contourner les exigences de transformation dbt :
  le code métier Silver et Gold reste en SQL dbt.

## Test de vérification

Charger deux fois le même lot et vérifier que la table Bronze conserve les deux
événements, que les tables Silver ne produisent aucun doublon métier, et que les
totaux Gold sont inchangés. C'est l'incident I01.
