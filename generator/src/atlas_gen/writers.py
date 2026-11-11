"""Écriture des lots et du manifeste.

Tout passe par ici pour garantir deux choses :
  - l'écriture est déterministe (colonnes ordonnées, pas d'horodatage machine
    dans le contenu métier) ;
  - chaque fichier produit sa ligne de manifeste avec son checksum.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Sequence


def checksum_fichier(chemin: Path) -> str:
    """SHA-256 du fichier, en hexadécimal."""
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


@dataclass
class EntreeManifeste:
    batch_id: str
    source: str
    mode: str
    schema_version: str
    file_name: str
    row_count: int
    checksum: str
    ordre_simulation: int
    anomalies: list[str] = field(default_factory=list)


@dataclass
class Manifeste:
    """Décrit les lots produits. Ne contient jamais la correction d'une anomalie."""

    seed: int
    profile: str
    scenario: str
    entrees: list[EntreeManifeste] = field(default_factory=list)

    def ajouter(self, entree: EntreeManifeste) -> None:
        self.entrees.append(entree)

    def ecrire(self, chemin: Path) -> None:
        charge = {
            "seed": self.seed,
            "profile": self.profile,
            "scenario": self.scenario,
            "batches": [asdict(e) for e in self.entrees],
        }
        chemin.write_text(
            json.dumps(charge, indent=2, ensure_ascii=False, sort_keys=False) + "\n",
            encoding="utf-8",
        )


def ecrire_csv(chemin: Path, colonnes: Sequence[str], lignes: Iterable[dict[str, Any]]) -> int:
    """Écrit un CSV UTF-8, colonnes dans l'ordre du contrat. Renvoie le nombre de lignes."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with chemin.open("w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=list(colonnes), lineterminator="\n")
        writer.writeheader()
        for ligne in lignes:
            writer.writerow({c: _texte(ligne.get(c)) for c in colonnes})
            n += 1
    return n


def ecrire_jsonl(chemin: Path, colonnes: Sequence[str], lignes: Iterable[dict[str, Any]]) -> int:
    """Écrit un JSONL, une ligne par enregistrement, clés dans l'ordre du contrat."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with chemin.open("w", encoding="utf-8", newline="\n") as f:
        for ligne in lignes:
            ordonne = {c: ligne.get(c) for c in colonnes if c in ligne}
            # Les colonnes hors contrat (métadonnées CDC) sont conservées à la fin.
            extra = {k: v for k, v in ligne.items() if k not in ordonne}
            f.write(json.dumps({**ordonne, **extra}, ensure_ascii=False) + "\n")
            n += 1
    return n


def _texte(valeur: Any) -> str:
    """Rend une valeur de façon stable en CSV. None devient une chaîne vide."""
    if valeur is None:
        return ""
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    return str(valeur)
