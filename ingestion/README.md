# Ingestion Bronze

Charge les fichiers produits par le générateur en tables Delta Bronze.

Responsabilités de cette couche :

- conserver le payload d'origine, sans aucune correction ;
- ajouter `file_name`, `row_number`, `record_hash` ;
- porter les métadonnées de lot : `batch_id`, `ingested_at`, `schema_version`,
  et le `checksum` du manifeste pour les sources FULL ;
- refuser un lot dont le checksum ne correspond pas au manifeste.

Ce qui n'appartient PAS à cette couche : typage métier, déduplication,
résolution de références, application de règles de gestion. Tout cela est du
ressort de dbt (voir `docs/decisions/001-separation-ingestion-dbt.md`).

## À implémenter en S3

- [ ] `charger_lot.py` : un lot, une source, vers une table Delta Bronze
- [ ] Vérification du checksum contre le manifeste avant chargement
- [ ] Mode FULL et mode CDC
- [ ] Registre d'exécution : `run_id`, lots, statut, compteurs
