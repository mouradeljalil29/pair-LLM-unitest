"""
Analyse des résultats expérimentaux.

Génère :
- agrégats par (llm, prompt) → tableau de synthèse
- boxplots de couverture par LLM
- heatmap couverture × complexité cyclomatique
- scatter plot mutation score vs branch coverage
- test statistique Mann-Whitney pour comparer les deux LLM

Usage : python -m analysis.stats
Tous les graphiques sont sauvegardés dans report/figures/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

FIG_DIR = Path("report/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="paper")


def load(csv_path: str = "results/metrics.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # types
    num_cols = ["line_coverage", "branch_coverage", "mutation_score",
                "n_assertions", "cc"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Agrégats moyennes ± écart-type par (LLM, prompt)."""
    agg = df.groupby(["llm", "prompt"]).agg(
        line_cov_mean=("line_coverage", "mean"),
        line_cov_std=("line_coverage", "std"),
        branch_cov_mean=("branch_coverage", "mean"),
        branch_cov_std=("branch_coverage", "std"),
        mutation_mean=("mutation_score", "mean"),
        syntax_err_rate=("syntax_error", "mean"),
        tests_passed_mean=("tests_passed", "mean"),
        cost_total=("cost_usd", "sum"),
    ).round(2)
    print("\n=== Tableau de synthèse ===")
    print(agg)
    agg.to_csv("report/summary.csv")
    return agg


def plot_coverage_boxplots(df: pd.DataFrame):
    """Boxplots de couverture par LLM (lignes et branches côte à côte)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    sns.boxplot(data=df, x="llm", y="line_coverage", hue="prompt", ax=axes[0])
    axes[0].set_title("Couverture lignes (%)")
    axes[0].set_ylim(0, 105)
    sns.boxplot(data=df, x="llm", y="branch_coverage", hue="prompt", ax=axes[1])
    axes[1].set_title("Couverture branches (%)")
    axes[1].set_ylim(0, 105)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "coverage_boxplots.png", dpi=150)
    plt.close()


def plot_coverage_vs_complexity(df: pd.DataFrame):
    """Heatmap : couverture moyenne par fonction × LLM, trié par CC."""
    pivot = (df.groupby(["function_id", "cc", "llm"])["branch_coverage"]
               .mean().reset_index()
               .pivot(index=["function_id", "cc"], columns="llm",
                      values="branch_coverage")
               .sort_index(level="cc"))
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="RdYlGn",
                vmin=0, vmax=100, ax=ax, cbar_kws={"label": "Branch cov. (%)"})
    ax.set_title("Couverture branches par fonction (triée par complexité)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "coverage_heatmap.png", dpi=150)
    plt.close()


def plot_mutation_vs_branch(df: pd.DataFrame):
    """Scatter : mutation score vs branch coverage (révèle les assertions superficielles)."""
    sub = df.dropna(subset=["mutation_score", "branch_coverage"])
    if sub.empty:
        print("Pas de données mutation, skip.")
        return
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.scatterplot(data=sub, x="branch_coverage", y="mutation_score",
                    hue="llm", style="prompt", s=80, ax=ax)
    ax.plot([0, 100], [0, 100], "k--", alpha=0.3, label="y = x")
    ax.set_xlabel("Couverture branches (%)")
    ax.set_ylabel("Mutation score (%)")
    ax.set_title("Mutation score vs couverture branches")
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 105)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mutation_vs_branch.png", dpi=150)
    plt.close()


def statistical_tests(df: pd.DataFrame):
    """
    Compare la couverture branches entre les 2 LLM avec Mann-Whitney U.
    Non paramétrique, adapté aux petits échantillons et aux distributions
    non gaussiennes (typique des % de couverture).
    """
    print("\n=== Tests statistiques (Mann-Whitney U) ===")
    llms = df["llm"].unique()
    if len(llms) != 2:
        print(f"Skipping: {len(llms)} LLM dans les données")
        return

    for prompt in df["prompt"].unique():
        sub = df[df["prompt"] == prompt]
        a = sub[sub["llm"] == llms[0]]["branch_coverage"].dropna()
        b = sub[sub["llm"] == llms[1]]["branch_coverage"].dropna()
        if len(a) == 0 or len(b) == 0:
            continue
        u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        # taille d'effet : r = Z / sqrt(N), approximation via U
        n = len(a) + len(b)
        z = (u - len(a) * len(b) / 2) / np.sqrt(len(a) * len(b) * (n + 1) / 12)
        r = abs(z) / np.sqrt(n)
        print(f"  Prompt={prompt}: {llms[0]}(med={a.median():.1f}) "
              f"vs {llms[1]}(med={b.median():.1f}) "
              f"→ U={u:.0f}, p={p:.4f}, r={r:.2f}")


def main():
    df = load()
    print(f"Chargé : {len(df)} runs")

    summary_table(df)
    plot_coverage_boxplots(df)
    plot_coverage_vs_complexity(df)
    plot_mutation_vs_branch(df)
    statistical_tests(df)
    print(f"\nFigures écrites dans {FIG_DIR}/")


if __name__ == "__main__":
    main()
