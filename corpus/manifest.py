"""
Manifeste central du corpus.

Une seule source de vérité pour : id, chemin, nom du module/symbole importable,
strate et complexité cyclomatique mesurée avec radon.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CorpusEntry:
    id: str
    strata: str
    source_path: str  # relatif à la racine du repo
    module_path: str  # forme dotted pour import dynamique
    symbol: str  # nom de la fonction/classe à tester
    cc: int  # complexité cyclomatique mesurée par radon


CORPUS = [
    # --- Strate 1 : simples ---
    CorpusEntry("f01", "simple", "corpus/simple/f01_is_palindrome.py",
                "corpus.simple.f01_is_palindrome", "is_palindrome", 4),
    CorpusEntry("f02", "simple", "corpus/simple/f02_fahrenheit_to_celsius.py",
                "corpus.simple.f02_fahrenheit_to_celsius", "fahrenheit_to_celsius", 4),
    CorpusEntry("f03", "simple", "corpus/simple/f03_validate_postal_code.py",
                "corpus.simple.f03_validate_postal_code", "validate_french_postal_code", 5),
    CorpusEntry("f04", "simple", "corpus/simple/f04_count_vowels.py",
                "corpus.simple.f04_count_vowels", "count_vowels", 4),
    CorpusEntry("f05", "simple", "corpus/simple/f05_clamp.py",
                "corpus.simple.f05_clamp", "clamp", 4),
    # --- Strate 2 : moyennes ---
    CorpusEntry("f06", "medium", "corpus/medium/f06_parse_iso_date.py",
                "corpus.medium.f06_parse_iso_date", "parse_iso_date", 5),
    CorpusEntry("f07", "medium", "corpus/medium/f07_merge_sorted_lists.py",
                "corpus.medium.f07_merge_sorted_lists", "merge_sorted_lists", 6),
    CorpusEntry("f08", "medium", "corpus/medium/f08_calculate_discount.py",
                "corpus.medium.f08_calculate_discount", "calculate_discount", 8),
    CorpusEntry("f09", "medium", "corpus/medium/f09_flatten_nested_dict.py",
                "corpus.medium.f09_flatten_nested_dict", "flatten_nested_dict", 2),
    CorpusEntry("f10", "medium", "corpus/medium/f10_roman_to_int.py",
                "corpus.medium.f10_roman_to_int", "roman_to_int", 9),
    # --- Strate 3 : complexes ---
    CorpusEntry("f11", "complex", "corpus/complex/f11_bank_account.py",
                "corpus.complex.f11_bank_account", "BankAccount", 4),
    CorpusEntry("f12", "complex", "corpus/complex/f12_tokenize_expression.py",
                "corpus.complex.f12_tokenize_expression", "tokenize_arithmetic_expression", 14),
    CorpusEntry("f13", "complex", "corpus/complex/f13_topological_sort.py",
                "corpus.complex.f13_topological_sort", "topological_sort", 5),
    CorpusEntry("f14", "complex", "corpus/complex/f14_match_glob_pattern.py",
                "corpus.complex.f14_match_glob_pattern", "match_glob_pattern", 12),
    CorpusEntry("f15", "complex", "corpus/complex/f15_rate_limiter.py",
                "corpus.complex.f15_rate_limiter", "RateLimiter", 5),
]


def get_source(entry: CorpusEntry) -> str:
    """Lit le code source de la fonction à tester."""
    with open(entry.source_path, encoding="utf-8") as f:
        return f.read()
