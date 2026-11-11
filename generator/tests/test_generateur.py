"""Contrôles indépendants du générateur.

Ces tests ne valident pas les transformations dbt : ils valident que les SOURCES
sont conformes au contrat et reproductibles. C'est le préalable à tout le reste.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from atlas_gen.cli import main
from atlas_gen.contracts import CONTRATS, TYPES_ANOMALIES
from atlas_gen.recette import construire_cas, verifier_coherence_interne
from atlas_gen.standard import generer


# --- Déterminisme -------------------------------------------------------------


def _checksums(repertoire: Path) -> dict[str, str]:
    manifeste = json.loads((repertoire / "manifest.json").read_text(encoding="utf-8"))
    return {b["source"]: b["checksum"] for b in manifeste["batches"]}


def test_micro_est_reproductible(tmp_path: Path) -> None:
    """Deux exécutions avec la même seed produisent des fichiers identiques."""
    a, b = tmp_path / "a", tmp_path / "b"
    assert main(["--seed", "42", "--profile", "MICRO", "--output-dir", str(a)]) == 0
    assert main(["--seed", "42", "--profile", "MICRO", "--output-dir", str(b)]) == 0
    assert _checksums(a) == _checksums(b)


def test_seed_differente_change_les_donnees() -> None:
    """Une seed différente doit produire un jeu différent, sinon la seed est ignorée."""
    un = generer(seed=42, profile="STANDARD", scenario="clean")
    deux = generer(seed=43, profile="STANDARD", scenario="clean")
    assert un["orders"][:50] != deux["orders"][:50]


def test_standard_est_reproductible() -> None:
    un = generer(seed=42, profile="STANDARD", scenario="clean")
    deux = generer(seed=42, profile="STANDARD", scenario="clean")
    assert un == deux


# --- Conformité au contrat ----------------------------------------------------


@pytest.mark.parametrize("source", sorted(CONTRATS))
def test_colonnes_du_contrat_presentes(source: str) -> None:
    """Chaque source produite porte au moins les colonnes minimales du contrat."""
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    if source not in donnees:
        pytest.skip(f"{source} n'est pas encore produit par le profil STANDARD")
    attendues = set(CONTRATS[source].colonnes)
    presentes = set(donnees[source][0])
    manquantes = attendues - presentes
    assert not manquantes, f"{source} : colonnes manquantes {sorted(manquantes)}"


def test_cles_uniques_sur_les_referentiels() -> None:
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    for source in ("stores", "crm_customers"):
        cle = CONTRATS[source].cle
        valeurs = [tuple(ligne[c] for c in cle) for ligne in donnees[source]]
        assert len(valeurs) == len(set(valeurs)), f"{source} : clé {cle} non unique"


def test_metadonnees_cdc_presentes_sur_les_sources_cdc() -> None:
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    for source, contrat in CONTRATS.items():
        if contrat.mode != "CDC" or source not in donnees or not donnees[source]:
            continue
        ligne = donnees[source][0]
        for champ in ("source_system", "entity_key", "op", "source_version", "event_ts"):
            assert champ in ligne, f"{source} : métadonnée CDC {champ} absente"


# --- Invariants métier du jeu propre ------------------------------------------


def test_intervalles_produits_sans_chevauchement() -> None:
    """Une clé naturelle n'a au maximum qu'une version ouverte."""
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    ouvertes: dict[str, int] = {}
    for version in donnees["product_versions"]:
        if version["effective_to"] is None:
            ouvertes[version["product_id"]] = ouvertes.get(version["product_id"], 0) + 1
    assert all(n == 1 for n in ouvertes.values())


def test_quantite_facturee_inferieure_ou_egale_a_commandee() -> None:
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    for ligne in donnees["order_lines"]:
        assert ligne["qty_invoiced"] <= ligne["qty_ordered"]


def test_pas_de_taux_eur_car_eur_vaut_un() -> None:
    """L'absence d'un taux EUR est normale : EUR vaut 1."""
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    assert all(t["currency"] != "EUR" for t in donnees["fx_rates"])


def test_volumes_dans_la_tolerance_de_dix_pourcent() -> None:
    donnees = generer(seed=42, profile="STANDARD", scenario="clean")
    assert 27000 <= len(donnees["orders"]) <= 33000
    assert len(donnees["crm_customers"]) == 6000
    assert len(donnees["stores"]) == 12


# --- Oracles de recette -------------------------------------------------------


def test_oracles_coherents_entre_eux() -> None:
    """Les identités comptables des attendus tiennent, indépendamment de dbt."""
    assert verifier_coherence_interne() == []


def test_t01_allocation_totalise_la_remise_de_commande() -> None:
    oracles = {o["cas"]: o["attendu"] for o in construire_cas()["oracles"]}
    t01 = oracles["T01"]
    total = Decimal(t01["allocation_L1"]) + Decimal(t01["allocation_L2"])
    assert total == Decimal("23.00")


def test_les_dix_cas_de_recette_sont_presents() -> None:
    cas = {o["cas"] for o in construire_cas()["oracles"]}
    assert cas == {f"T{i:02d}" for i in range(1, 11)}


def test_registre_des_anomalies_complet() -> None:
    """L'énoncé exige au moins 15 types d'anomalies."""
    assert len(set(TYPES_ANOMALIES)) >= 15
