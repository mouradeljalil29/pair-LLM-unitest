# Génération automatique de tests unitaires par LLM
*Projet PAIR 2025-2026 — ISEN Brest — DP Développement Logiciel*

Évaluation expérimentale comparant **GPT-4o-mini** (OpenAI) et **Claude Haiku 4.5** (Anthropic)
sur la génération de tests unitaires `pytest` pour un corpus de 15 fonctions Python
de complexité variable.

## Questions de recherche

- **RQ1** : Quelle couverture (lignes / branches) atteignent les tests générés par un LLM ?
- **RQ2** : Le type de prompt (zero-shot vs structuré) influence-t-il significativement les résultats ?
- **RQ3** : Les tests détectent-ils réellement des bugs (mutation testing) ou ne font-ils que passer ?
- **RQ4** : La complexité cyclomatique de la fonction impacte-t-elle la qualité des tests générés ?

## Hypothèses

- **H1** : Un prompt structuré produit une couverture branches supérieure d'au moins 10 points au zero-shot.
- **H2** : La couverture lignes est élevée (> 80 %) mais le mutation score reste faible (< 60 %),
  révélant des assertions superficielles.
- **H3** : La couverture chute significativement (> 20 pts) pour les fonctions de complexité cyclomatique ≥ 8.

## Design expérimental

```
2 LLM × 2 prompts × 15 fonctions × 3 répétitions = 180 générations
```

| Variable | Valeur |
|---|---|
| Modèles | gpt-4o-mini, claude-haiku-4-5 |
| Prompts | zero-shot, structuré |
| Température | 0.2 (fixe) |
| Répétitions | 3 par condition |
| Couverture | pytest-cov avec `--cov-branch` |
| Mutation | mutmut |

## Structure du repo

```
.
├── corpus/                # 15 fonctions sous test (3 strates de complexité)
│   ├── simple/            # CC 4-5
│   ├── medium/            # CC 5-9
│   ├── complex/           # CC 5-14
│   └── manifest.py        # métadonnées du corpus
├── prompts/               # zero_shot.txt, structured.txt
├── generators/            # wrappers OpenAI et Anthropic
├── runner/
│   ├── run_tests.py       # exécution pytest + collecte coverage
│   ├── run_mutation.py    # mutmut
│   └── evaluate.py        # orchestrateur principal
├── analysis/
│   ├── stats.py           # tableaux + graphiques + tests stat
│   └── qualitative_review.py  # grille de notation manuelle + kappa
├── results/
│   ├── raw/               # code des tests générés (un .py par run)
│   └── metrics.csv        # toutes les métriques collectées
└── report/
    ├── figures/           # graphiques pour le rapport
    └── rapport.md         # rapport scientifique
```

## Reproduction

```bash
# 1. Installer
pip install -r requirements.txt

# 2. Configurer les clés API
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Smoke test : 2 fonctions, 1 run, sans mutation (≈ 2 minutes)
python -m runner.evaluate --quick --runs 1

# 4. Expérience complète sans mutation testing (≈ 30-45 minutes)
python -m runner.evaluate --runs 3

# 5. Avec mutation testing (≈ 2-3 heures, à lancer la nuit)
python -m runner.evaluate --runs 3 --mutation

# 6. Analyse
python -m analysis.stats

# 7. Revue manuelle (toi et ton binôme)
python -m analysis.qualitative_review --sample 20 --judge mourad
python -m analysis.qualitative_review --sample 20 --judge <binome>
python -m analysis.qualitative_review --kappa
```

## Métriques collectées (par run)

| Métrique | Outil | Mesure |
|---|---|---|
| `line_coverage` | pytest-cov | % lignes exécutées |
| `branch_coverage` | pytest-cov --cov-branch | % branches couvertes |
| `mutation_score` | mutmut | % mutants tués |
| `tests_passed/failed` | pytest | fiabilité du code généré |
| `syntax_error` | parsing | tests qui ne compilent pas |
| `n_assertions` | regex sur AST | densité d'assertions |
| `tokens_in/out`, `cost_usd` | API | coût économique |

## Menaces à la validité (à documenter dans le rapport)

- **Contamination des données d'entraînement** des LLM (mitigation : fonctions custom dans le corpus).
- **Taille du corpus** (n=15) → résultats indicatifs, non généralisables.
- **Subjectivité de la revue qualitative** → mitigation : double-codage + Cohen's kappa.
- **Non-déterminisme** des LLM → mitigation : 3 répétitions par condition.
- **Évolution des modèles** : les résultats sont datés (préciser version + date).

## Équipe

- Mourad El Jalil
- [Nom du binôme]

Encadrant DP : Thierry Le Pors
