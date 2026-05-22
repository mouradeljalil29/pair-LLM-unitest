# Génération automatique de tests unitaires par LLM : évaluation empirique sur un mini corpus Python

**Mourad El Jalil, [Binôme]**
*ISEN Brest — DP Développement Logiciel — PAIR 2025-2026*
*Encadrant : Thierry Le Pors*

---

## Résumé

> **À rédiger en dernier.**
> 150-200 mots : problématique, méthode (corpus de 15 fonctions Python, 2 LLM, 2 prompts, 3 répétitions),
> résultats clés (chiffres précis), implications.

---

## 1. Introduction

### 1.1 Contexte

Les LLM (Large Language Models) comme GPT-4 et Claude sont de plus en plus utilisés pour automatiser
des tâches de génie logiciel, dont la génération de tests unitaires. La question de leur efficacité
réelle, au-delà de leur capacité à produire un code qui *semble* correct, reste néanmoins ouverte.

### 1.2 Problématique

*Dans quelle mesure un LLM génère-t-il des tests unitaires pertinents, à couverture élevée
et capables de détecter de vrais bugs, sur un corpus de fonctions Python de complexité variable ?*

### 1.3 Questions de recherche et hypothèses

- **RQ1** : Quelle couverture (lignes / branches) atteignent les tests générés ?
- **RQ2** : Le type de prompt influence-t-il significativement les résultats ?
- **RQ3** : Les tests détectent-ils des bugs (mutation testing) ou simplement *passent* ?
- **RQ4** : La complexité cyclomatique impacte-t-elle la qualité des tests ?

Trois hypothèses (à confirmer/infirmer) :
- **H1** : Prompt structuré → couverture branches supérieure de ≥ 10 points au zero-shot.
- **H2** : Couverture lignes > 80 % MAIS mutation score < 60 % (assertions superficielles).
- **H3** : Chute > 20 points de couverture pour CC ≥ 8.

---

## 2. État de l'art

> **À rédiger pendant les jours 1-2.**
> Couvrir au minimum :
> - Schäfer et al., *"An Empirical Evaluation of Using LLMs for Automated Unit Test Generation"* (TSE 2024).
> - Lemieux et al., *"CodaMosa: Escaping Coverage Plateaus in Test Generation with Pre-trained LLMs"* (ICSE 2023).
> - Outils académiques : ChatUniTest, TestPilot, AthenaTest.
> - Baselines non-LLM : EvoSuite (Java), Pynguin (Python).
> - Mutation testing comme proxy de qualité : Papadakis et al., *"Mutation Testing Advances"*.
> - Travaux récents sur la contamination des benchmarks (datasets que les LLM ont déjà vus).

Lacune identifiée justifiant notre travail : la majorité des évaluations existantes utilisent
des benchmarks publics (HumanEval, MBPP) potentiellement contaminés. Notre corpus mixte
(fonctions classiques + custom) cherche à limiter ce biais.

---

## 3. Méthodologie

### 3.1 Corpus

15 fonctions Python organisées en 3 strates de complexité cyclomatique mesurée avec `radon` :

| Strate | Fonctions | CC | Type |
|---|---|---|---|
| Simple | f01-f05 | 4-5 | Pures, peu de branches |
| Medium | f06-f10 | 2-9 | Branches métier, exceptions, récursion |
| Complex | f11-f15 | 4-14 | Classes stateful, parseurs, algorithmes |

*Choix méthodologique* : 1/3 environ des fonctions sont *custom* (ex. `validate_french_postal_code`,
`calculate_discount`, `RateLimiter`) pour réduire le biais de contamination de l'entraînement
des LLM. Les autres sont des classiques (palindrome, roman_to_int) pour permettre la comparaison
avec d'éventuels travaux futurs.

### 3.2 Modèles évalués

| Modèle | Provider | Date d'évaluation |
|---|---|---|
| gpt-4o-mini | OpenAI | [à compléter] |
| claude-haiku-4-5-20251001 | Anthropic | [à compléter] |

Température fixée à **0.2** pour limiter la variance tout en conservant la diversité naturelle
nécessaire à mesurer la robustesse.

### 3.3 Prompts comparés

- **Zero-shot** : instruction minimale (« Write unit tests in pytest for the following function »).
- **Structured** : instruction enrichie (couverture nominal / edge / error, parametrize, pas de fences).

### 3.4 Protocole expérimental

Design factoriel : **2 LLM × 2 prompts × 15 fonctions × 3 répétitions = 180 runs**.

Pour chaque run :
1. Génération via API LLM.
2. Sauvegarde du code brut généré (`results/raw/`).
3. Exécution sandboxée avec `pytest --cov-branch --cov-report=json`.
4. Mutation testing avec `mutmut`.
5. Toutes les métriques agrégées dans `results/metrics.csv`.

Une grille de notation qualitative (lisibilité, qualité des assertions, edge cases perçus,
maintenabilité) est appliquée sur un échantillon aléatoire stratifié de 20 fichiers,
codé indépendamment par les 2 membres du binôme. L'accord inter-juges est mesuré
par le **Cohen's kappa pondéré quadratique**.

### 3.5 Métriques

| Métrique | Outil | Interprétation |
|---|---|---|
| Couverture lignes | pytest-cov | Étendue d'exécution |
| Couverture branches | pytest-cov | Étendue logique réelle |
| Mutation score | mutmut | Capacité à détecter des bugs |
| % tests passants | pytest | Fiabilité du code généré |
| Taux d'erreurs syntaxiques | parsing | Inutilisabilité immédiate |
| Coût (tokens, $) | API logs | Faisabilité économique |

### 3.6 Analyse statistique

Comparaison des distributions de couverture entre les 2 LLM via le **test de Mann-Whitney U**
(non paramétrique, adapté aux petits échantillons et aux distributions non-normales).
Taille d'effet rapportée via *r* = |Z| / √N.

---

## 4. Résultats

### 4.1 Vue d'ensemble (RQ1)

> **À remplir après l'expé.** Insérer ici le tableau `report/summary.csv` et `figures/coverage_boxplots.png`.

Couverture moyenne par condition :

| LLM | Prompt | Lignes (moy ± σ) | Branches (moy ± σ) |
|---|---|---|---|
| gpt-4o-mini | zero-shot | ... | ... |
| gpt-4o-mini | structured | ... | ... |
| claude-haiku-4-5-20251001 | zero-shot | ... | ... |
| claude-haiku-4-5-20251001 | structured | ... | ... |

### 4.2 Effet du prompt (RQ2)

> Test Mann-Whitney sur zero-shot vs structured, par LLM.
> Conclusion sur H1.

### 4.3 Couverture vs détection réelle de bugs (RQ3)

> Insérer `figures/mutation_vs_branch.png`.
> Si tous les points sont sous la diagonale → confirmation de H2 (assertions superficielles).

### 4.4 Effet de la complexité (RQ4)

> Insérer `figures/coverage_heatmap.png`.
> Régression couverture ~ CC ou test stratifié simple/medium/complex.

### 4.5 Coût et temps de génération

> Tableau coûts totaux et temps moyens.

### 4.6 Analyse qualitative

> Résultats des 20 fichiers notés, kappa par critère, exemples illustratifs
> (un bon test, un mauvais test, un test qui passe mais ne teste rien).

---

## 5. Discussion

### 5.1 Réponses aux questions de recherche

> Reprendre RQ1-RQ4 et conclure sur H1-H3.

### 5.2 Implications pratiques

> - Confiance à accorder aux tests générés en l'état.
> - Importance du prompt engineering.
> - Workflow recommandé (génération + revue humaine).

### 5.3 Comparaison avec la littérature

> Cohérence ou divergence avec Schäfer et al., CodaMosa, etc.

---

## 6. Menaces à la validité

| Type | Menace | Mitigation |
|---|---|---|
| Construct | Le mutation score est-il un bon proxy de "détection de bugs" ? | Discussion + complément avec analyse manuelle |
| Internal | Non-déterminisme des LLM | 3 répétitions par condition |
| External | n=15, non généralisable | Énoncé explicite + diversité des strates |
| External | Contamination des données d'entraînement | 1/3 du corpus custom |
| Conclusion | Tests stat sur petit échantillon | Mann-Whitney non paramétrique + tailles d'effet |
| Construct | Subjectivité de la revue qualitative | Double-codage + Cohen's kappa |

---

## 7. Conclusion

> 150-200 mots. Rappel problématique, principal résultat, contribution, perspectives.

Perspectives :
- Étendre à un corpus de 50-100 fonctions.
- Inclure une baseline non-LLM (Pynguin) pour positionner l'apport réel des LLM.
- Étudier des prompts avancés (chain-of-thought, ReAct, génération itérative avec feedback de couverture).

---

## Références

> Format APA ou IEEE selon préférence du jury. À renseigner pendant la veille.

1. Schäfer, M., et al. (2024). An empirical evaluation of using large language models for
   automated unit test generation. *IEEE TSE*.
2. Lemieux, C., et al. (2023). CodaMosa: Escaping coverage plateaus in test generation with
   pre-trained large language models. *ICSE 2023*.
3. Papadakis, M., et al. (2019). Mutation testing advances: an analysis and survey.
   *Advances in Computers*, 112.

---

## Annexes

- **Annexe A** : Liste détaillée des 15 fonctions du corpus avec CC.
- **Annexe B** : Prompts complets (zero-shot et structuré).
- **Annexe C** : Tableau brut `metrics.csv` (lien GitHub).
- **Annexe D** : Exemples illustratifs (bon test, mauvais test, faux positif).
