"""
ID: f15
Strate: complex
Complexité cyclomatique attendue: 7
Notes: classe stateful time-based, custom (anti-contamination forte),
       teste la capacité du LLM à mocker le temps.
"""

import time


class RateLimiter:
    """
    Limiteur de débit à fenêtre glissante.

    Permet au plus `max_calls` appels par fenêtre de `window_seconds`.
    Le constructeur accepte un paramètre `time_provider` (callable
    retournant le temps courant en secondes) pour faciliter les tests.
    """

    def __init__(self, max_calls: int, window_seconds: float, time_provider=None):
        if max_calls <= 0:
            raise ValueError("max_calls doit être > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds doit être > 0")
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._time = time_provider if time_provider is not None else time.time
        self._calls = []

    def allow(self) -> bool:
        """
        Retourne True si l'appel est autorisé (et l'enregistre),
        False sinon (et n'enregistre pas l'appel).
        """
        now = self._time()
        cutoff = now - self.window_seconds
        # purge des appels hors fenêtre
        self._calls = [t for t in self._calls if t > cutoff]
        if len(self._calls) >= self.max_calls:
            return False
        self._calls.append(now)
        return True

    def remaining(self) -> int:
        """Retourne le nombre d'appels encore autorisés dans la fenêtre."""
        now = self._time()
        cutoff = now - self.window_seconds
        active = sum(1 for t in self._calls if t > cutoff)
        return max(0, self.max_calls - active)
