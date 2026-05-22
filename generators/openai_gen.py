"""
Générateur OpenAI.

Modèle par défaut : gpt-4o-mini (rapport qualité/prix excellent pour
notre usage). Tu peux passer à gpt-4o pour la comparaison "premium".

Tarifs (à vérifier au moment de l'expé sur https://openai.com/api/pricing/) :
- gpt-4o-mini : ~$0.15 / 1M input tokens, ~$0.60 / 1M output tokens
"""

import os
import time

from openai import OpenAI

from .base import GenerationResult, LLMGenerator, clean_code_fences


PRICING = {
    "gpt-4o-mini": (0.15 / 1_000_000, 0.60 / 1_000_000),
    "gpt-4o":      (2.50 / 1_000_000, 10.00 / 1_000_000),
}


class OpenAIGenerator(LLMGenerator):
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Variable d'environnement OPENAI_API_KEY non définie"
            )
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.name = model

    def generate(self, prompt: str) -> GenerationResult:
        start = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            elapsed = time.perf_counter() - start
            content = response.choices[0].message.content or ""
            usage = response.usage
            in_price, out_price = PRICING.get(self.model, (0, 0))
            cost = usage.prompt_tokens * in_price + usage.completion_tokens * out_price
            return GenerationResult(
                llm_name=self.name,
                prompt_name="",       # rempli par l'appelant
                function_id="",       # rempli par l'appelant
                run_id=0,             # rempli par l'appelant
                test_code=clean_code_fences(content),
                tokens_in=usage.prompt_tokens,
                tokens_out=usage.completion_tokens,
                generation_time_s=elapsed,
                cost_usd=cost,
            )
        except Exception as exc:  # noqa: BLE001
            return GenerationResult(
                llm_name=self.name,
                prompt_name="",
                function_id="",
                run_id=0,
                test_code="",
                tokens_in=0,
                tokens_out=0,
                generation_time_s=time.perf_counter() - start,
                cost_usd=0.0,
                error=f"{type(exc).__name__}: {exc}",
            )
