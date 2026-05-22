"""
Outil pour la revue manuelle qualitative des tests générés.

Tire un échantillon aléatoire stratifié de tests, propose une grille
de notation (1-5) sur 4 critères, et calcule l'accord inter-juges
(Cohen's kappa) entre toi et ton binôme.

Usage :
    1) python -m analysis.qualitative_review --sample 20 --judge mourad
    2) (ton binôme fait la même chose, --judge <son_prenom>)
    3) python -m analysis.qualitative_review --kappa
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

import pandas as pd


CRITERIA = {
    "readability":   "Lisibilité : noms de tests clairs, code propre (1=mauvais, 5=excellent)",
    "assertions":    "Qualité des assertions : précises, non triviales (1=trivial, 5=précis)",
    "edge_cases":    "Couverture des cas limites perçue (1=aucun, 5=exhaustif)",
    "maintainability": "Maintenabilité : DRY, parametrize, fixtures (1=copy-paste, 5=excellent)",
}


def sample_for_review(n: int, raw_dir: str = "results/raw",
                      seed: int = 42) -> list[Path]:
    """Échantillonne n fichiers générés aléatoirement (seed fixe = reproductible)."""
    files = sorted(Path(raw_dir).glob("*.py"))
    random.seed(seed)
    return random.sample(files, min(n, len(files)))


def conduct_review(judge: str, n: int):
    samples = sample_for_review(n)
    out_path = Path(f"results/review_{judge}.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Revue qualitative — juge: {judge} ===")
    print(f"Critères : {list(CRITERIA.keys())}\n")

    rows = []
    for i, path in enumerate(samples, 1):
        print(f"\n--- [{i}/{len(samples)}] {path.name} ---")
        print(path.read_text(encoding="utf-8")[:2000])  # tronqué pour l'affichage
        if len(path.read_text(encoding="utf-8")) > 2000:
            print("[... tronqué, voir le fichier ...]")

        scores = {"file": path.name, "judge": judge}
        for crit, desc in CRITERIA.items():
            while True:
                raw = input(f"  {desc}\n  Note (1-5) : ").strip()
                if raw in {"1", "2", "3", "4", "5"}:
                    scores[crit] = int(raw)
                    break
                print("  Saisir un entier entre 1 et 5")
        comment = input("  Commentaire libre (optionnel) : ").strip()
        scores["comment"] = comment
        rows.append(scores)

        # sauvegarde incrémentale
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(scores.keys()))
            w.writeheader()
            w.writerows(rows)

    print(f"\nRevue terminée. Notes enregistrées dans {out_path}")


def compute_kappa():
    """Calcule l'accord inter-juges Cohen's kappa entre les 2 reviewers."""
    files = list(Path("results").glob("review_*.csv"))
    if len(files) < 2:
        print("Il faut au moins 2 fichiers review_*.csv pour calculer kappa.")
        return

    dfs = [pd.read_csv(f) for f in files]
    # join sur le fichier noté pour aligner les paires de notes
    merged = dfs[0].merge(dfs[1], on="file", suffixes=("_j1", "_j2"))
    print(f"\n=== Cohen's kappa ({len(merged)} fichiers communs) ===")

    from sklearn.metrics import cohen_kappa_score  # import local
    for crit in CRITERIA:
        if f"{crit}_j1" in merged.columns and f"{crit}_j2" in merged.columns:
            k = cohen_kappa_score(
                merged[f"{crit}_j1"], merged[f"{crit}_j2"],
                weights="quadratic",
            )
            print(f"  {crit:20s} : kappa = {k:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--judge", type=str)
    ap.add_argument("--kappa", action="store_true")
    args = ap.parse_args()

    if args.kappa:
        compute_kappa()
    elif args.judge:
        conduct_review(args.judge, args.sample)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
