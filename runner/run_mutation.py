"""
Mutation testing avec mutmut.

Crée un dossier temporaire isolé contenant la fonction sous test
et les tests générés, puis lance mutmut. Calcule le mutation score
= mutants tués / mutants totaux.

ATTENTION : mutmut peut être lent (plusieurs minutes par fonction).
Limite l'usage à un sous-échantillon si le temps presse.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from corpus.manifest import CorpusEntry


@dataclass
class MutationMetrics:
    mutants_total: int = 0
    mutants_killed: int = 0
    mutants_survived: int = 0
    mutants_timeout: int = 0
    mutation_score: float = 0.0  # % tués sur total
    error: str = ""


def _patch_imports(test_code: str, entry: CorpusEntry) -> str:
    module_name = Path(entry.source_path).stem
    header = (
        f"import sys, os\n"
        f"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        f"from {module_name} import *  # noqa: F401, F403\n\n"
    )
    return header + test_code


def run_mutation_testing(
    test_code: str,
    entry: CorpusEntry,
    timeout_s: int = 300,
) -> MutationMetrics:
    """
    Lance mutmut sur la fonction du corpus avec les tests générés.
    """
    metrics = MutationMetrics()

    if not test_code.strip():
        metrics.error = "Code de test vide"
        return metrics

    workdir = Path(tempfile.mkdtemp(prefix=f"mut_{entry.id}_"))
    try:
        src_path = Path(entry.source_path).resolve()
        shutil.copy(src_path, workdir / src_path.name)

        patched = _patch_imports(test_code, entry)
        (workdir / f"test_generated_{entry.id}.py").write_text(
            patched, encoding="utf-8"
        )

        # config mutmut via setup.cfg (ciblage du module sous test)
        module_name = src_path.stem
        (workdir / "setup.cfg").write_text(
            f"[mutmut]\n"
            f"paths_to_mutate={module_name}.py\n"
            f"tests_dir=.\n"
            f"runner=python -m pytest -x --tb=no -q\n",
            encoding="utf-8",
        )

        try:
            subprocess.run(
                ["mutmut", "run"],
                cwd=workdir, timeout=timeout_s,
                capture_output=True, text=True,
            )
        except subprocess.TimeoutExpired:
            metrics.error = f"Timeout après {timeout_s}s"
            return metrics

        # parser les résultats avec `mutmut results`
        proc = subprocess.run(
            ["mutmut", "results"],
            cwd=workdir, capture_output=True, text=True, timeout=30,
        )
        output = proc.stdout

        # mutmut affiche par exemple :
        # "Killed 8" / "Survived 2" / "Timeout 0" etc.
        # On essaie deux patterns (les versions de mutmut diffèrent)
        for pat, attr in [
            (r"[Kk]illed[^\d]*(\d+)", "mutants_killed"),
            (r"[Ss]urvived[^\d]*(\d+)", "mutants_survived"),
            (r"[Tt]imeout[^\d]*(\d+)", "mutants_timeout"),
        ]:
            m = re.search(pat, output)
            if m:
                setattr(metrics, attr, int(m.group(1)))

        metrics.mutants_total = (
            metrics.mutants_killed
            + metrics.mutants_survived
            + metrics.mutants_timeout
        )
        if metrics.mutants_total > 0:
            metrics.mutation_score = (
                100.0 * metrics.mutants_killed / metrics.mutants_total
            )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    return metrics
