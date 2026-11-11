# Plan de réalisation

Version courte, tenue à jour dans le dépôt. La version détaillée et commentable
vit à part ; celle-ci fait foi pour l'équipe au quotidien.

## Les deux plafonds à sécuriser

L'énoncé prévoit deux conditions de qualité qui plafonnent la note collective,
quoi que vaille le reste du travail :

- CA ou marge incorrects sur T01 à T04, non expliqués et non corrigés : **10/20**
- aucune chaîne dbt exécutée sur Databricks démontrée : **8/20**

Ils se traitent en S1 et en S5, pas en S15.

## Principes

1. Sécuriser avant d'enrichir. Une chaîne minimale qui tourne de bout en bout
   vaut mieux que trois couches qui ne se connectent pas.
2. Chaque règle métier a son oracle indépendant, écrit avant le SQL.
3. Tout est scripté et rejouable. Aucune correction manuelle.
4. Chacun doit pouvoir expliquer le travail des autres : 25 % de la note est
   individuelle, et le jury interroge sur des parties écrites par d'autres.

## Phases et conditions de passage

| Phase | Semaines | Condition de passage |
| --- | --- | --- |
| Fondations | S1–S2 | `dbt debug` vert, chaîne MICRO démontrée, poste Windows confirmé |
| Données et contrats | S3–S4 | Lots reproductibles, anomalies quantifiées, grains relus |
| Silver et règles métier | S5–S6 | T01, T04, T05 et T08 verts, 20 contrôles exécutés |
| CDC et historisation | S7–S8 | Les trois exécutions convergent, rejeu et désordre réussis |
| Gold et publication | S9–S10 | 35 assertions, tous les cas MICRO, clôture V1 démontrée |
| Restitution | S11–S12 | Quatre pages, deux boards, cinq KPI concordants |
| Incidents, CI, performance | S13–S14 | 12 incidents rejouables, clôture V2, runbook |
| Gel et soutenance | S15–S16 | Reconstruction depuis le README, dépôt tagué `v1.0` |

## Répartition des axes

| Axe | Périmètre | Charge dominante |
| --- | --- | --- |
| A — Données et qualité | Générateur, 15 anomalies, manifestes, ingestion Bronze, oracles | S3–S6, puis incidents |
| B — Transformation et temporalité | dbt, Silver et Gold, CDC, incrémental, snapshots, publication | S5–S10 |
| C — Restitution et exploitation | Power BI, dbt Charts, concordance, runbook, CI, performance | S1, puis S11–S14 |

Le propriétaire d'un axe conçoit et écrit. Un membre d'un autre axe relit
systématiquement ses pull requests.

## Rituels

- Point de 30 minutes, deux fois par semaine.
- Démonstration interne de 15 minutes tous les quinze jours.
- Trois registres tenus dans le dépôt : backlog, arbitrages, risques.
- Avant chaque jalon, chacun explique un modèle écrit par quelqu'un d'autre.

## Risques suivis

| Risque | Parade | Échéance |
| --- | --- | --- |
| Pas de poste Windows pour Power BI | Poste réservé via l'établissement, VM en secours | S1 |
| Quota Databricks épuisé | 1 à 2 threads, profil STANDARD allégé validé, blocage documenté | continu |
| Règles T01–T04 fausses | Oracles avant le SQL, calculateur Python indépendant | S5 |
| Incrémental qui rate les corrections anciennes | Stratégie par clés impactées, test de convergence | S7–S8 |
| Dérive du périmètre | Aucune extension tant que les cas MICRO ne sont pas verts | continu |
| Un membre décroche techniquement | Revue croisée, séance d'explication avant chaque jalon | continu |
