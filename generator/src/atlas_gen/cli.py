"""Point d'entrée du générateur.

    python -m atlas_gen --seed 42 --profile MICRO --output-dir ../data/micro
    python -m atlas_gen --seed 42 --profile STANDARD --output-dir ../data/standard

Même seed et même profil produisent exactement les mêmes fichiers : le manifeste
porte les checksums, ce qui rend la propriété vérifiable sans lire les données.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import CONTRATS
from .recette import construire_cas, verifier_coherence_interne
from .standard import generer
from .writers import EntreeManifeste, Manifeste, checksum_fichier, ecrire_csv, ecrire_jsonl


def construire_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="atlas_gen", description="Générateur de sources Atlas Retail 360")
    p.add_argument("--seed", type=int, default=42, help="graine déterministe (référence : 42)")
    p.add_argument("--profile", choices=("MICRO", "STANDARD", "SCALE"), default="MICRO")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--scenario", default="clean", choices=("clean", "perturbed"))
    return p


def main(argv: list[str] | None = None) -> int:
    args = construire_parser().parse_args(argv)
    sortie: Path = args.output_dir
    sortie.mkdir(parents=True, exist_ok=True)

    manifeste = Manifeste(seed=args.seed, profile=args.profile, scenario=args.scenario)

    if args.profile == "MICRO":
        problemes = verifier_coherence_interne()
        if problemes:
            for p in problemes:
                print(f"INVARIANT ROMPU : {p}")
            return 1
        donnees = construire_cas()
        oracles = donnees.pop("oracles")
        (sortie / "oracles.json").write_text(
            json.dumps(oracles, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"  oracles.json              {len(oracles):>7} cas de recette")
    else:
        donnees = generer(args.seed, args.profile, args.scenario)

    for ordre, (source, lignes) in enumerate(sorted(donnees.items()), start=1):
        contrat = CONTRATS[source]
        batch_id = f"B{ordre:03d}-{args.profile.lower()}"
        colonnes = _colonnes_effectives(contrat.colonnes, lignes)
        nom = f"{source}.{'jsonl' if contrat.format == 'jsonl' else 'csv'}"
        chemin = sortie / nom

        if contrat.format == "jsonl":
            n = ecrire_jsonl(chemin, colonnes, lignes)
        else:
            # Parquet est produit en CSV tant que pyarrow n'est pas figé dans les
            # dépendances ; la bascule est tracée dans docs/decisions.
            n = ecrire_csv(chemin, colonnes, lignes)

        manifeste.ajouter(
            EntreeManifeste(
                batch_id=batch_id,
                source=source,
                mode=contrat.mode,
                schema_version="1.0",
                file_name=nom,
                row_count=n,
                checksum=checksum_fichier(chemin),
                ordre_simulation=ordre,
            )
        )
        print(f"  {nom:<26}{n:>7} lignes")

    manifeste.ecrire(sortie / "manifest.json")
    print(f"\nManifeste écrit : {sortie / 'manifest.json'}")
    return 0


def _colonnes_effectives(contrat: tuple[str, ...], lignes: list[dict[str, object]]) -> list[str]:
    """Colonnes du contrat, suivies des métadonnées réellement présentes."""
    colonnes = list(contrat)
    vues: list[str] = []
    for ligne in lignes:
        for cle in ligne:
            if cle not in colonnes and cle not in vues:
                vues.append(cle)
    return colonnes + vues


if __name__ == "__main__":
    raise SystemExit(main())
