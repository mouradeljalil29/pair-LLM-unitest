"""
Interface commune et dataclass de résultat pour les générateurs LLM.

L'objectif est qu'OpenAI et Anthropic exposent la MÊME signature pour
faciliter la boucle d'évaluation et garantir une comparaison équitable.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Résultat unique d'un appel à un LLM."""
    llm_name: str            # ex. "gpt-4o-mini"
    prompt_name: str         # "zero_shot" ou "structured"
    function_id: str         # ex. "f08"
    run_id: int              # numéro de répétition (0, 1, 2)
    test_code: str           # code Python brut renvoyé (nettoyé des fences)
    tokens_in: int
    tokens_out: int
    generation_time_s: float
    cost_usd: float          # estimé via les tarifs publics
    error: str = ""          # vide si OK, sinon message d'erreur


class LLMGenerator(ABC):
    """Contrat commun pour les générateurs."""

    name: str  # identifiant court utilisé dans les résultats

    @abstractmethod
    def generate(self, prompt: str) -> GenerationResult:
        """Envoie le prompt et retourne le résultat."""
        raise NotImplementedError


def clean_code_fences(text: str) -> str:
    """
    Retire les ```python / ``` éventuellement renvoyés par les LLM
    malgré une instruction explicite, et trim les espaces.
    """
    text = text.strip()
    if text.startswith("```"):
        # supprime la première ligne (```python ou ```)
        text = text.split("\n", 1)[1] if "\n" in text else ""
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()
