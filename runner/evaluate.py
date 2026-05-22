"""
Script principal d'évaluation.

Boucle sur le produit cartésien (LLM × prompt × fonction × run),
génère les tests, exécute pytest-cov et (optionnellement) mutmut,
puis écrit toutes les métriques dans results/metrics.csv.

Usage typique :
    python -m runner.evaluate --runs 3 --mutation
    python -m runner.evaluate --runs 1 --no-mutation --quick   # dry run rapide

Variables d'env requises :
    OPENAI_API_KEY, ANTHROPIC_API_KEY
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

# permet `python -m runner.evaluate` depuis la racine du repo
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from corpus.manifest import CORPUS, get_source  # noqa: E402
from generators.anthropic_gen import AnthropicGenerator  # noqa: E402
from generators.openai_gen import OpenAIGenerator  # noqa: E402
from runner.run_tests import run_generated_tests  # noqa: E402
from runner.run_mutation import run_mutation_testing  # noqa: E402


PROMPTS = {
    "zero_shot": Path("prompts/zero_shot.txt").read_text(encoding="utf-8"),
    "structured": Path("prompts/structured.txt").read_text(encoding="utf-8"),
}


CSV_FIELDS = [
    "function_id", "strata", "cc",
    "llm", "prompt", "run_id",
    "tests_collected", "tests_passed", "tests_failed", "tests_errored",
    "line_coverage", "branch_coverage",
    "mutation_score", "mutants_killed", "mutants_survived", "mutants_total",
    "n_assertions", "syntax_error", "timed_out",
    "tokens_in", "tokens_out", "generation_time_s", "cost_usd",
    "gen_error", "run_error",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3,
                    help="Nombre de répétitions par condition")
    ap.add_argument("--mutation", action="store_true",
                    help="Active le mutation testing (coûteux en temps)")
    ap.add_argument("--quick", action="store_true",
                    help="Mode test rapide : 2 premières fonctions seulement")
    ap.add_argument("--out", default="results/metrics.csv")
    ap.add_argument("--raw-dir", default="results/raw")
    args = ap.parse_args()

    Path(args.raw_dir).mkdir(parents=True, exist_ok=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    generators = [
        OpenAIGenerator(model="gpt-4o-mini"),
        AnthropicGenerator(model="claude-haiku-4-5"),
    ]
    corpus = CORPUS[:2] if args.quick else CORPUS

    rows = []
    total_iter = len(generators) * len(PROMPTS) * len(corpus) * args.runs
    iter_count = 0
    t_start = time.time()

    for entry in corpus:
        source = get_source(entry)
        for prompt_name, prompt_template in PROMPTS.items():
            full_prompt = prompt_template.replace("{code}", source)
            for gen in generators:
                for run_id in range(args.runs):
                    iter_count += 1
                    print(f"[{iter_count}/{total_iter}] "
                          f"{entry.id} | {gen.name} | {prompt_name} | run {run_id}")

                    # 1) Génération
                    gr = gen.generate(full_prompt)
                    gr.prompt_name = prompt_name
                    gr.function_id = entry.id
                    gr.run_id = run_id

                    # sauvegarde du code brut généré (utile pour debug + revue manuelle)
                    raw_filename = (
                        f"{entry.id}__{gen.name}__{prompt_name}__r{run_id}.py"
                    ).replace("/", "_")
                    raw_path = Path(args.raw_dir) / raw_filename
                    raw_path.write_text(gr.test_code or "", encoding="utf-8")

                    # 2) Exécution + couverture
                    exec_metrics = run_generated_tests(gr.test_code, entry)

                    # 3) Mutation testing (optionnel)
                    mut_metrics = None
                    if args.mutation and not exec_metrics.syntax_error:
                        mut_metrics = run_mutation_testing(gr.test_code, entry)

                    # 4) Assemblage de la ligne CSV
                    row = {
                        "function_id": entry.id,
                        "strata": entry.strata,
                        "cc": entry.cc,
                        "llm": gen.name,
                        "prompt": prompt_name,
                        "run_id": run_id,
                        "tests_collected": exec_metrics.tests_collected,
                        "tests_passed": exec_metrics.tests_passed,
                        "tests_failed": exec_metrics.tests_failed,
                        "tests_errored": exec_metrics.tests_errored,
                        "line_coverage": round(exec_metrics.line_coverage, 2),
                        "branch_coverage": round(exec_metrics.branch_coverage, 2),
                        "mutation_score": round(mut_metrics.mutation_score, 2) if mut_metrics else "",
                        "mutants_killed": mut_metrics.mutants_killed if mut_metrics else "",
                        "mutants_survived": mut_metrics.mutants_survived if mut_metrics else "",
                        "mutants_total": mut_metrics.mutants_total if mut_metrics else "",
                        "n_assertions": exec_metrics.n_assertions,
                        "syntax_error": exec_metrics.syntax_error,
                        "timed_out": exec_metrics.timed_out,
                        "tokens_in": gr.tokens_in,
                        "tokens_out": gr.tokens_out,
                        "generation_time_s": round(gr.generation_time_s, 2),
                        "cost_usd": round(gr.cost_usd, 6),
                        "gen_error": gr.error,
                        "run_error": exec_metrics.error_message,
                    }
                    rows.append(row)

                    # écriture incrémentale (au cas où l'expé crashe)
                    _write_csv(args.out, rows)

    elapsed = time.time() - t_start
    print(f"\nTerminé : {len(rows)} runs en {elapsed:.1f}s "
          f"({elapsed/max(len(rows),1):.1f}s/run)")
    print(f"Résultats : {args.out}")


def _write_csv(path: str, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
