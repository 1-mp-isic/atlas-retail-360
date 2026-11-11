"""Contrats de sources Atlas Retail 360.

Un seul endroit décrit les colonnes minimales de chaque source (sections 05 et 06
de l'énoncé). Le générateur et les contrôles indépendants lisent ce module, ce qui
évite qu'ils divergent silencieusement.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- Période métier ----------------------------------------------------------

PERIODE_DEBUT = "2024-09-01"
PERIODE_FIN = "2026-08-31"
SIMULATION_MOIS = "2026-09"

DEVISES = ("EUR", "CHF", "TND")
PAYS = ("FR", "CH", "TN")
CANAUX = ("MAGASIN", "WEB")
FAMILLES = ("F1", "F2", "F3", "F4", "F5", "F6")


@dataclass(frozen=True)
class Contrat:
    """Décrit une source : son format, son grain, sa clé et ses colonnes."""

    nom: str
    format: str
    grain: str
    cle: tuple[str, ...]
    colonnes: tuple[str, ...]
    mode: str  # FULL, CDC ou REFERENTIEL


# Métadonnées CDC obligatoires (section 06).
META_CDC = (
    "source_system",
    "entity_key",
    "op",
    "source_version",
    "event_ts",
    "ingested_at",
    "batch_id",
    "schema_version",
)

# Métadonnées des sources chargées en FULL.
META_FULL = ("batch_id", "extracted_at", "schema_version", "checksum")


CONTRATS: dict[str, Contrat] = {
    "orders": Contrat(
        nom="orders",
        format="jsonl",
        grain="une version d'une commande",
        cle=("order_id", "source_version"),
        colonnes=(
            "order_id",
            "customer_id",
            "store_id",
            "channel",
            "order_ts",
            "status",
            "currency",
            "campaign_id",
            "order_discount",
            "updated_at",
        ),
        mode="CDC",
    ),
    "order_lines": Contrat(
        nom="order_lines",
        format="csv",
        grain="une version d'une ligne de commande",
        cle=("order_id", "line_id", "source_version"),
        colonnes=(
            "order_id",
            "line_id",
            "product_id",
            "qty_ordered",
            "qty_invoiced",
            "unit_price_ht",
            "line_discount_ht",
            "invoice_ts",
            "is_cancelled",
            "updated_at",
        ),
        mode="CDC",
    ),
    "returns": Contrat(
        nom="returns",
        format="jsonl",
        grain="un événement de retour",
        cle=("return_id", "source_version"),
        colonnes=(
            "return_id",
            "order_id",
            "line_id",
            "return_ts",
            "qty_returned",
            "refund_ht",
            "restocked",
            "status",
            "updated_at",
        ),
        mode="CDC",
    ),
    "crm_customers": Contrat(
        nom="crm_customers",
        format="csv",
        grain="état courant complet d'un client",
        cle=("customer_id",),
        colonnes=(
            "customer_id",
            "country",
            "segment",
            "signup_date",
            "email_synthetic",
            "updated_at",
        ),
        mode="FULL",
    ),
    "customer_segment_events": Contrat(
        nom="customer_segment_events",
        format="jsonl",
        grain="un événement métier de segment",
        cle=("event_id",),
        colonnes=(
            "event_id",
            "customer_id",
            "segment",
            "effective_from",
            "source_version",
            "recorded_at",
        ),
        # Source d'événements métier : versionnée par source_version, mais sans
        # les métadonnées op/tombstone d'un flux CDC (section 05 de l'énoncé).
        mode="EVENEMENT",
    ),
    "product_versions": Contrat(
        nom="product_versions",
        format="parquet",
        grain="une version métier d'un produit",
        cle=("product_id", "effective_from"),
        colonnes=(
            "product_id",
            "family_id",
            "label",
            "unit_cost",
            "cost_currency",
            "effective_from",
            "effective_to",
            "updated_at",
        ),
        mode="REFERENTIEL",
    ),
    "stores": Contrat(
        nom="stores",
        format="csv",
        grain="un magasin",
        cle=("store_id",),
        colonnes=(
            "store_id",
            "country",
            "timezone",
            "opening_date",
            "closing_date",
            "label",
        ),
        mode="REFERENTIEL",
    ),
    "opening_stock": Contrat(
        nom="opening_stock",
        format="csv",
        grain="produit x magasin au 31/08/2024",
        cle=("product_id", "store_id"),
        colonnes=("product_id", "store_id", "opening_qty", "opening_ts"),
        mode="FULL",
    ),
    "stock_movements": Contrat(
        nom="stock_movements",
        format="csv",
        grain="un mouvement de stock",
        cle=("movement_id", "source_version"),
        colonnes=(
            "movement_id",
            "product_id",
            "store_id",
            "movement_ts",
            "movement_type",
            "qty_signed",
            "related_order_id",
            "related_return_id",
            "updated_at",
        ),
        mode="CDC",
    ),
    "fx_rates": Contrat(
        nom="fx_rates",
        format="csv",
        grain="devise x date de validité",
        cle=("currency", "rate_date"),
        colonnes=("currency", "rate_date", "eur_per_unit", "updated_at"),
        mode="REFERENTIEL",
    ),
    "budgets": Contrat(
        nom="budgets",
        format="csv",
        grain="mois x pays x canal x famille x version",
        cle=("month", "country", "channel", "family_id", "version"),
        colonnes=(
            "month",
            "country",
            "channel",
            "family_id",
            "version",
            "budget_ca_eur",
            "budget_margin_eur",
            "approved_at",
        ),
        mode="REFERENTIEL",
    ),
    "campaign_spend": Contrat(
        nom="campaign_spend",
        format="jsonl",
        grain="campagne x date x pays",
        cle=("campaign_id", "spend_date", "country"),
        colonnes=(
            "campaign_id",
            "spend_date",
            "country",
            "channel",
            "spend",
            "currency",
            "updated_at",
        ),
        mode="REFERENTIEL",
    ),
}


# Registre des 15 types d'anomalies exigés (section 04).
TYPES_ANOMALIES = (
    "doublon_exact",
    "doublon_conflictuel",
    "null_de_cle",
    "date_invalide",
    "montant_mal_forme",
    "reference_absente",
    "devise_inconnue",
    "taux_absent",
    "evenement_tardif",
    "evenement_desordonne",
    "suppression",
    "reactivation",
    "changement_de_schema",
    "retour_excessif",
    "stock_negatif",
)
