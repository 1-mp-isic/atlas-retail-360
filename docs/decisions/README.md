# Décisions d'architecture

Trois décisions minimales sont exigées par la section 09 de l'énoncé :
séparation ingestion / dbt, stratégie d'historisation, stratégie de publication.

Chaque décision décrit contexte, alternatives, choix, conséquences, et le test
qui permet de la vérifier. Une décision sans test de vérification n'est pas une
décision, c'est une intention.

| Fichier | Décision | Statut |
| --- | --- | --- |
| `001-separation-ingestion-dbt.md` | Où s'arrête l'ingestion, où commence dbt | acceptée |
| `002-strategie-historisation.md` | Comment les versions métier sont conservées | à rédiger |
| `003-strategie-publication.md` | Comment une version certifiée est publiée | à rédiger |
