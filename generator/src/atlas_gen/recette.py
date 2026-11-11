"""Profil MICRO : les cas de recette T01 à T10 de la section 18.

Deux choses sont produites ici, et elles doivent rester séparées :

  1. les ENTRÉES, écrites comme des sources brutes normales ;
  2. les ATTENDUS (oracles), écrits à la main depuis l'énoncé.

Les attendus ne sont jamais calculés par le code de transformation. C'est
exactement ce que demande l'énoncé : « copier la même expression de production
dans un test ne démontre pas sa justesse ».
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

SCHEMA_VERSION = "1.0"


def _order(order_id: str, **kw: Any) -> dict[str, Any]:
    base = {
        "order_id": order_id,
        "customer_id": kw.get("customer_id", "C001"),
        "store_id": kw.get("store_id", "S01"),
        "channel": kw.get("channel", "MAGASIN"),
        "order_ts": kw.get("order_ts", "2025-03-10T10:00:00+01:00"),
        "status": kw.get("status", "CONFIRMED"),
        "currency": kw.get("currency", "EUR"),
        "campaign_id": kw.get("campaign_id"),
        "order_discount": kw.get("order_discount", "0"),
        "updated_at": kw.get("updated_at", "2025-03-10T10:00:00+01:00"),
        "source_system": "POS",
        "entity_key": order_id,
        "op": kw.get("op", "I"),
        "source_version": kw.get("source_version", 1),
        "event_ts": kw.get("order_ts", "2025-03-10T10:00:00+01:00"),
        "schema_version": SCHEMA_VERSION,
    }
    return base


def _line(order_id: str, line_id: str, **kw: Any) -> dict[str, Any]:
    return {
        "order_id": order_id,
        "line_id": line_id,
        "product_id": kw.get("product_id", "P001"),
        "qty_ordered": kw.get("qty_ordered", kw.get("qty_invoiced", 1)),
        "qty_invoiced": kw.get("qty_invoiced", 1),
        "unit_price_ht": kw.get("unit_price_ht", "100"),
        "line_discount_ht": kw.get("line_discount_ht", "0"),
        "invoice_ts": kw.get("invoice_ts", "2025-03-10T11:00:00+01:00"),
        "is_cancelled": kw.get("is_cancelled", False),
        "updated_at": kw.get("updated_at", "2025-03-10T11:00:00+01:00"),
        "source_system": "POS",
        "entity_key": f"{order_id}|{line_id}",
        "op": kw.get("op", "I"),
        "source_version": kw.get("source_version", 1),
        "event_ts": kw.get("invoice_ts", "2025-03-10T11:00:00+01:00"),
        "schema_version": SCHEMA_VERSION,
    }


def _retour(return_id: str, order_id: str, line_id: str, **kw: Any) -> dict[str, Any]:
    return {
        "return_id": return_id,
        "order_id": order_id,
        "line_id": line_id,
        "return_ts": kw.get("return_ts", "2025-03-20T10:00:00+01:00"),
        "qty_returned": kw.get("qty_returned", 1),
        "refund_ht": kw.get("refund_ht", "0"),
        "restocked": kw.get("restocked", True),
        "status": kw.get("status", "ACCEPTED"),
        "updated_at": kw.get("updated_at", "2025-03-20T10:00:00+01:00"),
        "source_system": "POS",
        "entity_key": return_id,
        "op": "I",
        "source_version": kw.get("source_version", 1),
        "event_ts": kw.get("return_ts", "2025-03-20T10:00:00+01:00"),
        "schema_version": SCHEMA_VERSION,
    }


def _version_produit(product_id: str, effective_from: str, unit_cost: str, **kw: Any) -> dict[str, Any]:
    return {
        "product_id": product_id,
        "family_id": kw.get("family_id", "F1"),
        "label": kw.get("label", f"Produit {product_id}"),
        "unit_cost": unit_cost,
        "cost_currency": kw.get("cost_currency", "EUR"),
        "effective_from": effective_from,
        "effective_to": kw.get("effective_to"),
        "updated_at": kw.get("updated_at", "2024-08-31T00:00:00+00:00"),
    }


def construire_cas() -> dict[str, Any]:
    """Construit les entrées et les attendus des cas T01 à T10.

    Les montants attendus sont recopiés de l'énoncé, pas recalculés.
    """
    orders: list[dict[str, Any]] = []
    lines: list[dict[str, Any]] = []
    returns: list[dict[str, Any]] = []
    produits: list[dict[str, Any]] = []
    mouvements: list[dict[str, Any]] = []
    fx: list[dict[str, Any]] = []
    budgets: list[dict[str, Any]] = []
    oracles: list[dict[str, Any]] = []

    # --- T01 : remise globale répartie au prorata -----------------------------
    # L1 : 2 x 100, remise ligne 20  -> base 180
    # L2 : 1 x 50                     -> base 50
    # remise commande 23 -> allocations 18 et 5
    orders.append(_order("T01", order_discount="23"))
    lines.append(_line("T01", "L1", product_id="PT01A", qty_invoiced=2, unit_price_ht="100", line_discount_ht="20"))
    lines.append(_line("T01", "L2", product_id="PT01B", qty_invoiced=1, unit_price_ht="50"))
    produits.append(_version_produit("PT01A", "2024-01-01", "60"))
    produits.append(_version_produit("PT01B", "2024-01-01", "20"))
    oracles.append(
        {
            "cas": "T01",
            "libelle": "Remise globale répartie au prorata",
            "attendu": {
                "base_L1": "180.00",
                "base_L2": "50.00",
                "allocation_L1": "18.00",
                "allocation_L2": "5.00",
                "vente_L1": "162.00",
                "vente_L2": "45.00",
                "ca_net_eur": "207.00",
                "cout_net_eur": "140.00",
                "marge_eur": "67.00",
            },
        }
    )

    # --- T02 : retour remis en stock ------------------------------------------
    orders.append(_order("T02", order_discount="23"))
    lines.append(_line("T02", "L1", product_id="PT01A", qty_invoiced=2, unit_price_ht="100", line_discount_ht="20"))
    lines.append(_line("T02", "L2", product_id="PT01B", qty_invoiced=1, unit_price_ht="50"))
    returns.append(_retour("R-T02", "T02", "L1", qty_returned=1, refund_ht="81", restocked=True))
    oracles.append(
        {
            "cas": "T02",
            "libelle": "Retour accepté, remis en stock",
            "attendu": {
                "a_la_date_du_retour": {"ca_eur": "-81.00", "cout_net_eur": "-60.00", "marge_eur": "-21.00"},
                "cumul_vente_et_retour": {"ca_eur": "126.00", "cout_net_eur": "80.00", "marge_eur": "46.00"},
            },
        }
    )

    # --- T03 : retour non remis en stock --------------------------------------
    orders.append(_order("T03", order_discount="23"))
    lines.append(_line("T03", "L1", product_id="PT01A", qty_invoiced=2, unit_price_ht="100", line_discount_ht="20"))
    lines.append(_line("T03", "L2", product_id="PT01B", qty_invoiced=1, unit_price_ht="50"))
    returns.append(_retour("R-T03", "T03", "L1", qty_returned=1, refund_ht="81", restocked=False))
    oracles.append(
        {
            "cas": "T03",
            "libelle": "Retour accepté, perdu (non restocké)",
            "attendu": {
                "cumul_vente_et_retour": {"ca_eur": "126.00", "cout_net_eur": "140.00", "marge_eur": "-14.00"},
            },
        }
    )

    # --- T04 : conversion CHF -> EUR ------------------------------------------
    orders.append(_order("T04", currency="CHF", store_id="S05"))
    lines.append(_line("T04", "L1", product_id="PT04", qty_invoiced=1, unit_price_ht="100"))
    produits.append(_version_produit("PT04", "2024-01-01", "60", cost_currency="CHF"))
    fx.append({"currency": "CHF", "rate_date": "2025-03-10", "eur_per_unit": "1.05", "updated_at": "2025-03-10T00:00:00+00:00"})
    oracles.append(
        {
            "cas": "T04",
            "libelle": "Conversion au taux de la date de facture",
            "attendu": {"ca_eur": "105.00", "cout_eur": "63.00", "marge_eur": "42.00"},
        }
    )

    # --- T05 : stock, idempotence du rejeu ------------------------------------
    mouvements.extend(
        [
            {
                "movement_id": "M-T05-0",
                "product_id": "PT05",
                "store_id": "S01",
                "movement_ts": "2024-08-31T23:00:00+02:00",
                "movement_type": "OPENING",
                "qty_signed": 10,
                "related_order_id": None,
                "related_return_id": None,
                "updated_at": "2024-08-31T23:00:00+02:00",
                "source_system": "WMS",
                "entity_key": "M-T05-0",
                "op": "I",
                "source_version": 1,
                "event_ts": "2024-08-31T23:00:00+02:00",
                "schema_version": SCHEMA_VERSION,
            },
            {
                "movement_id": "M-T05-1",
                "product_id": "PT05",
                "store_id": "S01",
                "movement_ts": "2025-03-01T09:00:00+01:00",
                "movement_type": "RECEIPT",
                "qty_signed": 5,
                "related_order_id": None,
                "related_return_id": None,
                "updated_at": "2025-03-01T09:00:00+01:00",
                "source_system": "WMS",
                "entity_key": "M-T05-1",
                "op": "I",
                "source_version": 1,
                "event_ts": "2025-03-01T09:00:00+01:00",
                "schema_version": SCHEMA_VERSION,
            },
            {
                "movement_id": "M-T05-2",
                "product_id": "PT05",
                "store_id": "S01",
                "movement_ts": "2025-03-05T09:00:00+01:00",
                "movement_type": "SALE",
                "qty_signed": -4,
                "related_order_id": "T05",
                "related_return_id": None,
                "updated_at": "2025-03-05T09:00:00+01:00",
                "source_system": "WMS",
                "entity_key": "M-T05-2",
                "op": "I",
                "source_version": 1,
                "event_ts": "2025-03-05T09:00:00+01:00",
                "schema_version": SCHEMA_VERSION,
            },
            {
                "movement_id": "M-T05-3",
                "product_id": "PT05",
                "store_id": "S01",
                "movement_ts": "2025-03-08T09:00:00+01:00",
                "movement_type": "RETURN_RESTOCK",
                "qty_signed": 1,
                "related_order_id": "T05",
                "related_return_id": "R-T05",
                "updated_at": "2025-03-08T09:00:00+01:00",
                "source_system": "WMS",
                "entity_key": "M-T05-3",
                "op": "I",
                "source_version": 1,
                "event_ts": "2025-03-08T09:00:00+01:00",
                "schema_version": SCHEMA_VERSION,
            },
        ]
    )
    oracles.append(
        {
            "cas": "T05",
            "libelle": "Stock fin de journée et idempotence du rejeu",
            "attendu": {"stock_final": 12, "stock_apres_rejeu_du_meme_lot": 12},
        }
    )

    # --- T06 : ligne annulée ---------------------------------------------------
    orders.append(_order("T06"))
    lines.append(_line("T06", "L1", product_id="PT01A", qty_invoiced=2, unit_price_ht="100", is_cancelled=True))
    oracles.append(
        {
            "cas": "T06",
            "libelle": "Ligne annulée avec quantité facturée",
            "attendu": {
                "ca_eur": "0.00",
                "cout_eur": "0.00",
                "anomalie_attendue": "coherence_ligne_annulee_avec_qty_invoiced",
            },
        }
    )

    # --- T07 : CDC désordonné --------------------------------------------------
    # versions 1 puis 3 puis 2 : la 2 arrive en dernier et ne doit pas gagner.
    orders.append(_order("T07"))
    lines.append(_line("T07", "L1", product_id="PT07", unit_price_ht="100", source_version=1, op="I"))
    lines.append(_line("T07", "L1", product_id="PT07", unit_price_ht="120", source_version=3, op="U"))
    lines.append(_line("T07", "L1", product_id="PT07", unit_price_ht="110", source_version=2, op="U"))
    produits.append(_version_produit("PT07", "2024-01-01", "50"))
    oracles.append(
        {
            "cas": "T07",
            "libelle": "Version CDC ancienne reçue en dernier",
            "attendu": {"unit_price_ht_courant": "120", "nb_lignes_metier": 1},
        }
    )

    # --- T08 : atteinte du budget au bon grain ---------------------------------
    orders.append(_order("T08A", order_ts="2025-04-03T10:00:00+02:00"))
    lines.append(
        _line("T08A", "L1", product_id="PT08", qty_invoiced=1, unit_price_ht="60", invoice_ts="2025-04-03T11:00:00+02:00")
    )
    orders.append(_order("T08B", order_ts="2025-04-12T10:00:00+02:00"))
    lines.append(
        _line("T08B", "L1", product_id="PT08", qty_invoiced=1, unit_price_ht="40", invoice_ts="2025-04-12T11:00:00+02:00")
    )
    produits.append(_version_produit("PT08", "2024-01-01", "10", family_id="F2"))
    budgets.append(
        {
            "month": "2025-04",
            "country": "FR",
            "channel": "MAGASIN",
            "family_id": "F2",
            "version": "V1",
            "budget_ca_eur": "200",
            "budget_margin_eur": "120",
            "approved_at": "2025-03-25T00:00:00+00:00",
        }
    )
    oracles.append(
        {
            "cas": "T08",
            "libelle": "Atteinte du budget au grain mois x pays x canal x famille",
            "attendu": {"ca_eur": "100.00", "budget_eur": "200.00", "atteinte_pct": "50.00", "piege": "jamais 25 %"},
        }
    )

    # --- T09 : validité métier du coût produit ---------------------------------
    orders.append(_order("T09", order_ts="2025-01-15T09:00:00+01:00"))
    lines.append(
        _line("T09", "L1", product_id="PT09", qty_invoiced=2, unit_price_ht="80", invoice_ts="2025-01-15T10:00:00+01:00")
    )
    produits.append(_version_produit("PT09", "2024-01-01", "40", effective_to="2025-01-15"))
    produits.append(_version_produit("PT09", "2025-01-15", "50"))
    oracles.append(
        {
            "cas": "T09",
            "libelle": "Vente le jour du changement de coût",
            "attendu": {"cout_eur": "100.00", "ca_eur": "160.00", "marge_eur": "60.00", "nb_versions_jointes": 1},
        }
    )

    # --- T10 : taux hors de la fenêtre de 7 jours ------------------------------
    orders.append(_order("T10", currency="CHF", store_id="S05", order_ts="2025-01-10T09:00:00+01:00"))
    lines.append(
        _line("T10", "L1", product_id="PT04", qty_invoiced=1, unit_price_ht="200", invoice_ts="2025-01-10T10:00:00+01:00")
    )
    fx.append({"currency": "CHF", "rate_date": "2025-01-02", "eur_per_unit": "1.04", "updated_at": "2025-01-02T00:00:00+00:00"})
    oracles.append(
        {
            "cas": "T10",
            "libelle": "Aucun taux dans la fenêtre de 7 jours",
            "attendu": {
                "ca_eur_certifie": None,
                "comportement": "quarantaine, montant source conservé, certification du périmètre bloquée",
                "montant_source": "200 CHF",
            },
        }
    )

    return {
        "orders": orders,
        "order_lines": lines,
        "returns": returns,
        "product_versions": produits,
        "stock_movements": mouvements,
        "fx_rates": fx,
        "budgets": budgets,
        "oracles": oracles,
    }


def verifier_coherence_interne() -> list[str]:
    """Contrôle d'invariants sur les oracles, indépendant de toute transformation.

    Revérifie à la main les deux identités comptables de T01 et T02 pour que
    personne ne puisse modifier un attendu sans s'en apercevoir.
    """
    problemes: list[str] = []
    cas = {o["cas"]: o["attendu"] for o in construire_cas()["oracles"]}

    t01 = cas["T01"]
    if Decimal(t01["ca_net_eur"]) != Decimal(t01["vente_L1"]) + Decimal(t01["vente_L2"]):
        problemes.append("T01 : le CA net ne vaut pas la somme des ventes de lignes")
    if Decimal(t01["allocation_L1"]) + Decimal(t01["allocation_L2"]) != Decimal("23"):
        problemes.append("T01 : les allocations ne totalisent pas la remise de commande")
    if Decimal(t01["marge_eur"]) != Decimal(t01["ca_net_eur"]) - Decimal(t01["cout_net_eur"]):
        problemes.append("T01 : marge differente de CA net moins cout net")

    t02 = cas["T02"]["cumul_vente_et_retour"]
    if Decimal(t02["marge_eur"]) != Decimal(t02["ca_eur"]) - Decimal(t02["cout_net_eur"]):
        problemes.append("T02 : marge differente de CA net moins cout net")

    return problemes
