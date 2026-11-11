# Fiche d'accès par produit

Exigée par la section 03 bis de l'énoncé. Revue au lancement, puis avant la
livraison. Une indisponibilité ou un quota fournisseur documenté ici ne pénalise
pas la note.

Dernière revue : à compléter · Prochaine revue : avant la livraison S15

## Synthèse

| Produit | Édition | Version | Compte | Authentification | Limite connue | Coût | Test S1 | Repli |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Databricks | Free Edition | à relever | un par étudiant | jeton personnel | compute serverless, quotas, pas de réseau privé | gratuit | à faire | workspace institutionnel validé par l'enseignant |
| dbt Core | open source | à figer | — | — | — | gratuit | à faire | — |
| dbt-databricks | adaptateur | à figer | — | jeton Databricks | suit les limites Databricks | gratuit | à faire | — |
| Python | CPython | 3.11+ | — | — | — | gratuit | à faire | — |
| Git / GitHub | — | — | un par étudiant | SSH ou jeton | — | gratuit | à faire | — |
| Power BI Desktop | gratuit | à relever | compte local | — | **Windows uniquement** | gratuit | à faire | poste de l'établissement, ou VM Windows |
| Power BI Service | — | — | — | — | publication soumise à licence | non fourni | sans objet | non exigé par l'énoncé |
| dbt Charts (dct) | local, open source | à figer | — | jeton Databricks si connexion directe | à vérifier | gratuit | à faire | export CSV ou Parquet certifié |
| pytest | — | à figer | — | — | — | gratuit | à faire | — |
| SQLFluff | — | à figer | — | — | — | gratuit | à faire | — |

## Détail par produit

### Databricks Free Edition

- Inscription : <https://docs.databricks.com/aws/en/getting-started/free-edition>
- Limitations à vérifier : <https://docs.databricks.com/aws/en/getting-started/free-edition-limitations>
- Un compte par étudiant. Aucun partage de compte ni de jeton entre membres.
- Si la collaboration dans un workspace est limitée, chacun travaille sur son
  compte et le groupe synchronise le code et les lots par Git.
- À relever et noter ici : `host`, `http_path`, catalogue et schéma utilisés.

Résultat du test de faisabilité :

- [ ] Workspace créé, membre A
- [ ] Workspace créé, membre B
- [ ] Workspace créé, membre C
- [ ] Table Delta créée
- [ ] Deux modèles et un test exécutés
- [ ] Deux captures d'un snapshot

### dbt Core et dbt-databricks

- Connexion documentée : <https://docs.databricks.com/aws/en/partners/prep/dbt>
- Versions figées dans `generator/pyproject.toml` et `dbt_project/packages.yml`.

Résultat du test :

- [ ] `dbt debug` vert, avec capture d'écran datée
- [ ] `dbt deps` réussi
- [ ] `dbt build --select tag:silver` réussi

### Power BI Desktop

- Téléchargement : <https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop>
- Licences : <https://learn.microsoft.com/en-us/power-bi/fundamentals/end-user-license>
- Connecteur Databricks : <https://learn.microsoft.com/en-us/power-query/connectors/databricks-azure>
- **Point bloquant à traiter en S1** : Power BI Desktop ne fonctionne que sous
  Windows. Identifier le poste utilisé par le groupe et le noter ici.

Poste Windows retenu : à compléter

Résultat du test :

- [ ] Power BI Desktop installé
- [ ] Connexion au SQL warehouse testée (hostname, HTTP Path, authentification)
- [ ] Un mart importé

### dbt Charts

- Documentation : <https://docs.dbtcharts.com/>
- Installation : <https://docs.dbtcharts.com/guides/installation/>
- Installer dans un environnement isolé : `uv tool install "dbt-charts[databricks]"`
- Figer la version retenue et la noter ici.

Résultat du test :

- [ ] `dct` installé, version notée
- [ ] Un board rendu sur le même mart que Power BI

## Journal des blocages

| Date | Produit | Blocage observé | Action | Statut |
| --- | --- | --- | --- | --- |
| | | | | |

## Demandes adressées à l'enseignant

| Date | Demande | Réponse | Statut |
| --- | --- | --- | --- |
| | Supports de cours de la matière | | en attente |
| | Validation d'un profil STANDARD allégé si les quotas l'exigent | | en attente |
| | Confirmation de la disponibilité d'un poste Windows | | en attente |
