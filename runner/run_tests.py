"""
Exécution sandboxée des tests générés et collecte des métriques de couverture.

Chaque test généré est exécuté dans un dossier temporaire isolé, avec :
- la fonction sous test copiée à côté
- un import auto-injecté (le LLM ne le met pas toujours bien)
- un timeout pour se protéger des boucles infinies
- pytest-cov avec --cov-branch pour les couvertures lignes ET branches
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from corpus.manifest import CorpusEntry, get_source


@dataclass
class ExecutionMetrics:
    tests_collected: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_errored: int = 0
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    n_assertions: int = 0
    runtime_s: float = 0.0
    timed_out: bool = False
    syntax_error: bool = False
    error_message: str = ""


def _count_assertions(test_code: str) -> int:
    """
    Heuristique simple : compte les `assert` au début de ligne
    (insensible à l'indentation), incluant les `assert ` et `assert(`.
    """
    return len(re.findall(r"^\s*assert\b", test_code, re.MULTILINE))


def _patch_imports(test_code: str, entry: CorpusEntry) -> str:
    """
    S'assure que le module sous test est importable.

    Le LLM va souvent générer `from f08_calculate_discount import ...`
    ou `from corpus.medium.f08_calculate_discount import ...`. On normalise
    en injectant un import « catch-all » au début du fichier de test.
    """
    module_name = Path(entry.source_path).stem  # ex. f08_calculate_discount
    header = (
        f"# Auto-injected import shim\n"
        f"import sys, os\n"
        f"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        f"from {module_name} import *  # noqa: F401, F403\n\n"
    )
    return header + test_code


def run_generated_tests(
    test_code: str,
    entry: CorpusEntry,
    timeout_s: int = 60,
) -> ExecutionMetrics:
    """
    Exécute le code de test généré contre la fonction du corpus.
    Retourne des métriques de couverture (lignes + branches).
    """
    metrics = ExecutionMetrics()
    metrics.n_assertions = _count_assertions(test_code)

    if not test_code.strip():
        metrics.error_message = "Code de test vide"
        return metrics

    workdir = Path(tempfile.mkdtemp(prefix=f"pair_{entry.id}_"))
    try:
        # copier la fonction sous test
        src_path = Path(entry.source_path).resolve()
        shutil.copy(src_path, workdir / src_path.name)

        # écrire le fichier de test
        patched = _patch_imports(test_code, entry)
        test_path = workdir / f"test_generated_{entry.id}.py"
        test_path.write_text(patched, encoding="utf-8")

        # exécuter pytest avec couverture (lignes + branches)
        module_under_test = src_path.stem
        cov_json = workdir / "coverage.json"
        cmd = [
            "python", "-m", "pytest",
            str(test_path),
            f"--cov={module_under_test}",
            "--cov-branch",
            f"--cov-report=json:{cov_json}",
            "--tb=short", "-q",
            "-p", "no:cacheprovider",
        ]
        try:
            result = subprocess.run(
                cmd, cwd=workdir, timeout=timeout_s,
                capture_output=True, text=True,
            )
        except subprocess.TimeoutExpired:
            metrics.timed_out = True
            metrics.error_message = f"Timeout après {timeout_s}s"
            return metrics

        # parser stdout pytest pour passed/failed/errors
        stdout = result.stdout
        for pat, attr in [
            (r"(\d+) passed", "tests_passed"),
            (r"(\d+) failed", "tests_failed"),
            (r"(\d+) error", "tests_errored"),
        ]:
            m = re.search(pat, stdout)
            if m:
                setattr(metrics, attr, int(m.group(1)))
        metrics.tests_collected = (
            metrics.tests_passed + metrics.tests_failed + metrics.tests_errored
        )

        # détecter une SyntaxError : pytest peut soit refuser de collecter,
        # soit la lister comme une erreur de collection (1 errored sans test passé/failed).
        if (
            "SyntaxError" in stdout
            or "SyntaxError" in result.stderr
            or "IndentationError" in stdout
            or "IndentationError" in result.stderr
        ):
            metrics.syntax_error = True
            metrics.error_message = "SyntaxError dans le code généré"

        # parser le rapport JSON de coverage
        if cov_json.exists():
            try:
                with open(cov_json) as f:
                    cov_data = json.load(f)
                totals = cov_data.get("totals", {})
                metrics.line_coverage = totals.get("percent_covered", 0.0)
                covered_branches = totals.get("covered_branches", 0)
                total_branches = totals.get("num_branches", 0)
                metrics.branch_coverage = (
                    100.0 * covered_branches / total_branches
                    if total_branches > 0
                    else 0.0
                )
            except (json.JSONDecodeError, KeyError) as exc:
                metrics.error_message = f"Parse coverage failed: {exc}"

    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    return metrics


def metrics_to_dict(m: ExecutionMetrics) -> dict:
    return asdict(m)
