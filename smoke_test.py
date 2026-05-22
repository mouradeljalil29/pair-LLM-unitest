"""
Smoke test sans clé API : vérifie que la chaîne
[code de test fictif] → [pytest-cov] → [métriques] fonctionne.

À lancer depuis la racine du repo :
    python smoke_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from corpus.manifest import CORPUS, get_source
from runner.run_tests import run_generated_tests

# Tests "parfaits" écrits à la main pour f01 (palindrome)
# permet de vérifier qu'on peut effectivement atteindre 100% de coverage
GOLDEN_F01 = '''
import pytest

def test_simple_palindrome():
    assert is_palindrome("aba") is True

def test_not_palindrome():
    assert is_palindrome("abc") is False

def test_empty_string():
    assert is_palindrome("") is True

def test_ignore_case():
    assert is_palindrome("AbA") is True

def test_ignore_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama") is True

def test_non_string_raises():
    with pytest.raises(TypeError):
        is_palindrome(42)
'''

# Tests "buggés" : un import incorrect → doit déclencher syntax_error/no tests
BAD_TESTS = '''
def test_broken(
    assert False
'''

if __name__ == "__main__":
    f01 = next(e for e in CORPUS if e.id == "f01")

    print(f"=== Smoke test 1 : tests parfaits sur {f01.id} ===")
    m = run_generated_tests(GOLDEN_F01, f01)
    print(f"  tests collectés: {m.tests_collected}")
    print(f"  passed: {m.tests_passed}, failed: {m.tests_failed}, errored: {m.tests_errored}")
    print(f"  line coverage: {m.line_coverage:.1f}%")
    print(f"  branch coverage: {m.branch_coverage:.1f}%")
    print(f"  assertions: {m.n_assertions}")

    assert m.tests_passed == 6, f"Attendu 6 tests passants, obtenu {m.tests_passed}"
    assert m.line_coverage > 90, f"Couverture lignes trop basse: {m.line_coverage}"
    print("  ✅ OK\n")

    print(f"=== Smoke test 2 : code de test buggé sur {f01.id} ===")
    m = run_generated_tests(BAD_TESTS, f01)
    print(f"  syntax_error détectée: {m.syntax_error}")
    print(f"  tests collectés: {m.tests_collected}")
    assert m.syntax_error or m.tests_collected == 0, "Devrait détecter l'erreur"
    print("  ✅ OK\n")

    print("=== Smoke test 3 : import du corpus complet ===")
    for entry in CORPUS:
        src = get_source(entry)
        assert len(src) > 0
        assert entry.symbol in src
    print(f"  ✅ Les {len(CORPUS)} fonctions du corpus sont accessibles")

    print("\n🎉 Pipeline OK — prêt pour l'expé avec de vraies clés API.")
