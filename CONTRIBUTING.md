# Travailler sur ce dépôt

## Branches

Une branche par fonctionnalité, nommée `axe-<a|b|c>/<sujet-court>`.
Exemple : `axe-b/allocation-remise`.

## Avant d'ouvrir une pull request

```bash
./scripts/valider.sh
```

## Revue

Toute pull request est relue par un membre d'un **autre axe** que le sien.
La revue laisse un commentaire de fond, pas un « OK ». C'est à la fois une
exigence de l'énoncé et la préparation directe aux questions individuelles de
la soutenance, où chacun doit expliquer le travail des autres.

Un changement de métrique ou de contrat de source exige une revue avant
intégration, sans exception.

## Messages de commit

Format court : `<axe>: <ce qui change>`.
Exemple : `axe-a: ajoute les 15 types d'anomalies au générateur`.

Le journal de contribution individuel de chacun s'appuie sur cet historique.
Tenez-le au fil de l'eau, pas en S16.
