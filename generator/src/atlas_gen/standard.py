"""Profil STANDARD : jeu de données synthétique complet et déterministe.

Déterminisme : un seul objet `random.Random(seed)` est utilisé, et les boucles
parcourent toujours les entités dans le même ordre. Aucune horloge système
n'intervient dans le contenu métier.

Volumes de référence de l'énoncé (± 10 % sur les faits) :
  30 000 commandes, ~60 000 lignes, 6 000 clients, 1 000 produits,
  12 magasins, 120 000 mouvements de stock.
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from .contracts import CANAUX, FAMILLES, PERIODE_DEBUT, PERIODE_FIN

SCHEMA_VERSION = "1.0"

# 12 magasins : 5 FR, 4 CH, 2 TN et 1 centre web.
MAGASINS = [
    {"store_id": "S01", "country": "FR", "timezone": "Europe/Paris", "label": "Paris Rivoli"},
    {"store_id": "S02", "country": "FR", "timezone": "Europe/Paris", "label": "Lyon Part-Dieu"},
    {"store_id": "S03", "country": "FR", "timezone": "Europe/Paris", "label": "Lille Grand Place"},
    {"store_id": "S04", "country": "FR", "timezone": "Europe/Paris", "label": "Bordeaux Sainte-Catherine"},
    {"store_id": "S05", "country": "CH", "timezone": "Europe/Zurich", "label": "Genève Rive"},
    {"store_id": "S06", "country": "CH", "timezone": "Europe/Zurich", "label": "Lausanne Flon"},
    {"store_id": "S07", "country": "CH", "timezone": "Europe/Zurich", "label": "Zurich Bahnhofstrasse"},
    {"store_id": "S08", "country": "TN", "timezone": "Africa/Tunis", "label": "Tunis Lac"},
    {"store_id": "S09", "country": "TN", "timezone": "Africa/Tunis", "label": "Sousse Corniche"},
    {"store_id": "S10", "country": "FR", "timezone": "Europe/Paris", "label": "Marseille Prado"},
    {"store_id": "S11", "country": "CH", "timezone": "Europe/Zurich", "label": "Bâle Marktplatz"},
    {"store_id": "W01", "country": "FR", "timezone": "Europe/Paris", "label": "Centre e-commerce"},
]

DEVISE_PAR_PAYS = {"FR": "EUR", "CH": "CHF", "TN": "TND"}

VOLUMES = {
    "MICRO": {"commandes": 0, "clients": 0, "produits": 0},
    "STANDARD": {"commandes": 30000, "clients": 6000, "produits": 1000},
    "SCALE": {"commandes": 300000, "clients": 60000, "produits": 10000},
}


def _jours(debut: str, fin: str) -> list[date]:
    d0 = date.fromisoformat(debut)
    d1 = date.fromisoformat(fin)
    return [d0 + timedelta(days=i) for i in range((d1 - d0).days + 1)]


def _iso(d: date, heure: int, minute: int, offset_h: int) -> str:
    tz = timezone(timedelta(hours=offset_h))
    return datetime(d.year, d.month, d.day, heure, minute, tzinfo=tz).isoformat()


def _offset(store: dict[str, Any], d: date) -> int:
    """Offset simplifié : heure d'été d'avril à octobre pour FR et CH."""
    if store["country"] == "TN":
        return 1
    return 2 if 4 <= d.month <= 10 else 1


def generer(seed: int, profile: str, scenario: str) -> dict[str, list[dict[str, Any]]]:
    """Produit toutes les sources du profil demandé. Même seed, mêmes données."""
    rng = random.Random(seed)
    vol = VOLUMES[profile]
    jours = _jours(PERIODE_DEBUT, PERIODE_FIN)

    magasins = [
        {
            "store_id": m["store_id"],
            "country": m["country"],
            "timezone": m["timezone"],
            "opening_date": "2024-01-01",
            "closing_date": "2026-03-31" if m["store_id"] == "S11" else None,
            "label": m["label"],
        }
        for m in MAGASINS
    ]

    produits, versions = _produits(rng, vol["produits"])
    clients, evenements_segment = _clients(rng, vol["clients"], jours)
    fx = _fx(rng, jours)
    commandes, lignes, retours = _ventes(rng, vol["commandes"], jours, magasins, produits, clients, scenario)
    couples, ouverture, mouvements = _stock(rng, magasins, produits, lignes, commandes, retours)
    budgets = _budgets(rng, jours)
    depenses = _campagnes(rng, jours)

    return {
        "stores": magasins,
        "product_versions": versions,
        "crm_customers": clients,
        "customer_segment_events": evenements_segment,
        "fx_rates": fx,
        "orders": commandes,
        "order_lines": lignes,
        "returns": retours,
        "opening_stock": ouverture,
        "stock_movements": mouvements,
        "budgets": budgets,
        "campaign_spend": depenses,
    }


def _produits(rng: random.Random, n: int) -> tuple[list[str], list[dict[str, Any]]]:
    ids = [f"P{i:04d}" for i in range(1, n + 1)]
    versions: list[dict[str, Any]] = []
    for pid in ids:
        famille = FAMILLES[int(pid[1:]) % len(FAMILLES)]
        cout = Decimal(rng.randrange(500, 9000)) / Decimal(100)
        versions.append(
            {
                "product_id": pid,
                "family_id": famille,
                "label": f"Article {pid}",
                "unit_cost": f"{cout:.2f}",
                "cost_currency": "EUR",
                "effective_from": "2024-01-01",
                "effective_to": None,
                "updated_at": "2024-01-01T00:00:00+00:00",
            }
        )
        # Un produit sur cinq change de coût en cours de période.
        if rng.random() < 0.2:
            bascule = "2025-07-01"
            versions[-1]["effective_to"] = bascule
            nouveau = cout * Decimal("1.08")
            versions.append(
                {
                    "product_id": pid,
                    "family_id": famille,
                    "label": f"Article {pid}",
                    "unit_cost": f"{nouveau:.2f}",
                    "cost_currency": "EUR",
                    "effective_from": bascule,
                    "effective_to": None,
                    "updated_at": "2025-06-25T00:00:00+00:00",
                }
            )
    return ids, versions


def _clients(rng: random.Random, n: int, jours: list[date]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    segments = ("STANDARD", "PREMIUM", "VIP")
    clients: list[dict[str, Any]] = []
    evenements: list[dict[str, Any]] = []
    for i in range(1, n + 1):
        cid = f"C{i:05d}"
        pays = ("FR", "CH", "TN")[i % 3]
        inscription = jours[rng.randrange(0, len(jours))]
        segment = segments[rng.randrange(0, len(segments))]
        clients.append(
            {
                "customer_id": cid,
                "country": pays,
                "segment": segment,
                "signup_date": inscription.isoformat(),
                "email_synthetic": f"{cid.lower()}@exemple-fictif.test",
                "updated_at": f"{inscription.isoformat()}T00:00:00+00:00",
            }
        )
        evenements.append(
            {
                "event_id": f"E{i:06d}-1",
                "customer_id": cid,
                "segment": "STANDARD",
                "effective_from": inscription.isoformat(),
                "source_version": 1,
                "recorded_at": f"{inscription.isoformat()}T00:00:00+00:00",
            }
        )
        # Un client sur dix change de segment en cours de mois (cas imposé).
        if rng.random() < 0.1 and segment != "STANDARD":
            bascule = jours[min(len(jours) - 1, jours.index(inscription) + rng.randrange(30, 400))]
            evenements.append(
                {
                    "event_id": f"E{i:06d}-2",
                    "customer_id": cid,
                    "segment": segment,
                    "effective_from": bascule.isoformat(),
                    "source_version": 2,
                    "recorded_at": f"{bascule.isoformat()}T00:00:00+00:00",
                }
            )
    return clients, evenements


def _fx(rng: random.Random, jours: list[date]) -> list[dict[str, Any]]:
    taux: list[dict[str, Any]] = []
    chf, tnd = Decimal("1.05"), Decimal("0.29")
    for j in jours:
        chf += (Decimal(rng.randrange(-20, 21)) / Decimal(10000))
        tnd += (Decimal(rng.randrange(-10, 11)) / Decimal(10000))
        for devise, valeur in (("CHF", chf), ("TND", tnd)):
            taux.append(
                {
                    "currency": devise,
                    "rate_date": j.isoformat(),
                    "eur_per_unit": f"{valeur:.4f}",
                    "updated_at": f"{j.isoformat()}T00:00:00+00:00",
                }
            )
    return taux


def _ventes(
    rng: random.Random,
    n: int,
    jours: list[date],
    magasins: list[dict[str, Any]],
    produits: list[str],
    clients: list[dict[str, Any]],
    scenario: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    commandes: list[dict[str, Any]] = []
    lignes: list[dict[str, Any]] = []
    retours: list[dict[str, Any]] = []

    for i in range(1, n + 1):
        oid = f"O{i:06d}"
        store = magasins[rng.randrange(0, len(magasins))]
        j = jours[rng.randrange(0, len(jours))]
        off = _offset(store, j)
        canal = "WEB" if store["store_id"] == "W01" else CANAUX[0]
        devise = DEVISE_PAR_PAYS[store["country"]]
        # 12 % de commandes anonymes : exclues des ratios d'identité.
        client = None if rng.random() < 0.12 else clients[rng.randrange(0, len(clients))]["customer_id"]
        campagne = f"CMP{rng.randrange(1, 13):02d}" if rng.random() < 0.3 else None
        nb_lignes = 1 + (i % 3)

        bases: list[Decimal] = []
        lignes_commande: list[dict[str, Any]] = []
        for k in range(1, nb_lignes + 1):
            pid = produits[rng.randrange(0, len(produits))]
            qty_cmd = rng.randrange(1, 5)
            # Les commandes en attente ne créent pas de revenu.
            en_attente = rng.random() < 0.05
            qty_fac = 0 if en_attente else (qty_cmd if rng.random() < 0.85 else rng.randrange(1, qty_cmd + 1))
            prix = Decimal(rng.randrange(900, 25000)) / Decimal(100)
            remise = (prix * Decimal(qty_fac) * Decimal("0.1")).quantize(Decimal("0.01")) if rng.random() < 0.25 else Decimal("0")
            annulee = rng.random() < 0.03
            base = (prix * Decimal(qty_fac) - remise) if (qty_fac > 0 and not annulee) else Decimal("0")
            bases.append(base)
            lignes_commande.append(
                {
                    "order_id": oid,
                    "line_id": f"L{k}",
                    "product_id": pid,
                    "qty_ordered": qty_cmd,
                    "qty_invoiced": qty_fac,
                    "unit_price_ht": f"{prix:.2f}",
                    "line_discount_ht": f"{remise:.2f}",
                    "invoice_ts": None if qty_fac == 0 else _iso(j, 11, 0, off),
                    "is_cancelled": annulee,
                    "updated_at": _iso(j, 11, 0, off),
                    "source_system": "POS",
                    "entity_key": f"{oid}|L{k}",
                    "op": "I",
                    "source_version": 1,
                    "event_ts": _iso(j, 11, 0, off),
                    "schema_version": SCHEMA_VERSION,
                }
            )

        total_base = sum(bases)
        remise_cmd = (total_base * Decimal("0.05")).quantize(Decimal("0.01")) if (total_base > 0 and rng.random() < 0.2) else Decimal("0")
        statut = "PENDING" if total_base == 0 else "CONFIRMED"

        commandes.append(
            {
                "order_id": oid,
                "customer_id": client,
                "store_id": store["store_id"],
                "channel": canal,
                "order_ts": _iso(j, 10, 0, off),
                "status": statut,
                "currency": devise,
                "campaign_id": campagne,
                "order_discount": f"{remise_cmd:.2f}",
                "updated_at": _iso(j, 10, 0, off),
                "source_system": "POS",
                "entity_key": oid,
                "op": "I",
                "source_version": 1,
                "event_ts": _iso(j, 10, 0, off),
                "schema_version": SCHEMA_VERSION,
            }
        )
        lignes.extend(lignes_commande)

        # 7 % des lignes facturées donnent lieu à un retour accepté.
        for ligne, base in zip(lignes_commande, bases):
            if base > 0 and rng.random() < 0.07:
                jr = jours[min(len(jours) - 1, jours.index(j) + rng.randrange(3, 40))]
                qty_ret = 1
                remboursement = (base / Decimal(max(1, ligne["qty_invoiced"]))).quantize(Decimal("0.01"))
                retours.append(
                    {
                        "return_id": f"R{len(retours) + 1:06d}",
                        "order_id": oid,
                        "line_id": ligne["line_id"],
                        "return_ts": _iso(jr, 14, 0, _offset(store, jr)),
                        "qty_returned": qty_ret,
                        "refund_ht": f"{remboursement:.2f}",
                        "restocked": rng.random() < 0.8,
                        "status": "ACCEPTED" if rng.random() < 0.9 else "REJECTED",
                        "updated_at": _iso(jr, 14, 0, _offset(store, jr)),
                        "source_system": "POS",
                        "entity_key": f"R{len(retours) + 1:06d}",
                        "op": "I",
                        "source_version": 1,
                        "event_ts": _iso(jr, 14, 0, _offset(store, jr)),
                        "schema_version": SCHEMA_VERSION,
                    }
                )

    return commandes, lignes, retours


def _stock(
    rng: random.Random,
    magasins: list[dict[str, Any]],
    produits: list[str],
    lignes: list[dict[str, Any]],
    commandes: list[dict[str, Any]],
    retours: list[dict[str, Any]],
) -> tuple[list[tuple[str, str]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Stock d'ouverture et mouvements sur environ 1 500 couples produit-magasin actifs."""
    cible = min(1500, len(produits) * len(magasins))
    couples: list[tuple[str, str]] = []
    vus: set[tuple[str, str]] = set()
    i = 0
    while len(couples) < cible and i < cible * 10:
        pid = produits[rng.randrange(0, len(produits))]
        sid = magasins[rng.randrange(0, len(magasins))]["store_id"]
        if (pid, sid) not in vus:
            vus.add((pid, sid))
            couples.append((pid, sid))
        i += 1

    ouverture = [
        {
            "product_id": pid,
            "store_id": sid,
            "opening_qty": rng.randrange(20, 200),
            "opening_ts": "2024-08-31T23:59:59+00:00",
        }
        for pid, sid in couples
    ]

    store_par_commande = {c["order_id"]: c["store_id"] for c in commandes}
    mouvements: list[dict[str, Any]] = []

    def ajouter(pid: str, sid: str, ts: str, type_mvt: str, qty: int, oid: str | None, rid: str | None) -> None:
        mid = f"M{len(mouvements) + 1:07d}"
        mouvements.append(
            {
                "movement_id": mid,
                "product_id": pid,
                "store_id": sid,
                "movement_ts": ts,
                "movement_type": type_mvt,
                "qty_signed": qty,
                "related_order_id": oid,
                "related_return_id": rid,
                "updated_at": ts,
                "source_system": "WMS",
                "entity_key": mid,
                "op": "I",
                "source_version": 1,
                "event_ts": ts,
                "schema_version": SCHEMA_VERSION,
            }
        )

    for ligne in lignes:
        if ligne["qty_invoiced"] and not ligne["is_cancelled"] and ligne["invoice_ts"]:
            sid = store_par_commande.get(ligne["order_id"])
            if sid and (ligne["product_id"], sid) in vus:
                ajouter(ligne["product_id"], sid, ligne["invoice_ts"], "SALE", -int(ligne["qty_invoiced"]), ligne["order_id"], None)

    produit_par_ligne = {(l["order_id"], l["line_id"]): l["product_id"] for l in lignes}
    for retour in retours:
        if retour["status"] == "ACCEPTED" and retour["restocked"]:
            pid = produit_par_ligne.get((retour["order_id"], retour["line_id"]))
            sid = store_par_commande.get(retour["order_id"])
            if pid and sid and (pid, sid) in vus:
                ajouter(pid, sid, retour["return_ts"], "RETURN_RESTOCK", int(retour["qty_returned"]), retour["order_id"], retour["return_id"])

    # Réceptions de réapprovisionnement pour atteindre l'ordre de grandeur attendu.
    cibles_receptions = max(0, 120000 - len(mouvements)) if len(produits) >= 1000 else len(couples) * 4
    jours_reappro = _jours(PERIODE_DEBUT, PERIODE_FIN)
    for _ in range(cibles_receptions):
        pid, sid = couples[rng.randrange(0, len(couples))]
        j = jours_reappro[rng.randrange(0, len(jours_reappro))]
        ajouter(pid, sid, f"{j.isoformat()}T06:00:00+00:00", "RECEIPT", rng.randrange(5, 60), None, None)

    mouvements.sort(key=lambda m: (m["movement_ts"], m["movement_id"]))
    return couples, ouverture, mouvements


def _budgets(rng: random.Random, jours: list[date]) -> list[dict[str, Any]]:
    mois = sorted({j.strftime("%Y-%m") for j in jours})
    lignes: list[dict[str, Any]] = []
    for m in mois:
        for pays in ("FR", "CH", "TN"):
            for canal in CANAUX:
                for famille in FAMILLES:
                    ca = Decimal(rng.randrange(20000, 150000))
                    lignes.append(
                        {
                            "month": m,
                            "country": pays,
                            "channel": canal,
                            "family_id": famille,
                            "version": "V1",
                            "budget_ca_eur": f"{ca:.2f}",
                            "budget_margin_eur": f"{ca * Decimal('0.35'):.2f}",
                            "approved_at": f"{m}-01T00:00:00+00:00",
                        }
                    )
    return lignes


def _campagnes(rng: random.Random, jours: list[date]) -> list[dict[str, Any]]:
    depenses: list[dict[str, Any]] = []
    for j in jours:
        for n in range(1, 13):
            if rng.random() < 0.12:
                pays = ("FR", "CH", "TN")[n % 3]
                depenses.append(
                    {
                        "campaign_id": f"CMP{n:02d}",
                        "spend_date": j.isoformat(),
                        "country": pays,
                        "channel": CANAUX[n % 2],
                        "spend": f"{Decimal(rng.randrange(10000, 200000)) / Decimal(100):.2f}",
                        "currency": DEVISE_PAR_PAYS[pays],
                        "updated_at": f"{j.isoformat()}T00:00:00+00:00",
                    }
                )
    return depenses
