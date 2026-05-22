"""
Générateur Anthropic (Claude).

Modèle par défaut : claude-haiku-4-5 (rapide, économique) ;
tu peux passer à claude-sonnet-4-5 pour la version "premium".

Vérifie les modèles disponibles et tarifs courants sur :
https://docs.claude.com/en/docs/about-claude/models

Tarifs indicatifs (à confirmer au moment de l'expé) :
- claude-haiku-4-5 : ~$1.00 / 1M input, ~$5.00 / 1M output
- claude-sonnet-4-5 : ~$3.00 / 1M input, ~$15.00 / 1M output
"""

import os
import time

import anthropic

from .base import GenerationResult, LLMGenerator, clean_code_fences


PRICING = {
    "claude-haiku-4-5-20251001":  (1.00 / 1_000_000, 5.00 / 1_000_000),
    "claude-sonnet-4-5-20251001": (3.00 / 1_000_000, 15.00 / 1_000_000),
}


class AnthropicGenerator(LLMGenerator):
    def __init__(self, model: str = "claude-haiku-4-5-20251001", temperature: float = 0.2):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Variable d'environnement ANTHROPIC_API_KEY non définie"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.name = model

    def generate(self, prompt: str) -> GenerationResult:
        start = time.perf_counter()
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            elapsed = time.perf_counter() - start
            # le SDK renvoie une liste de content blocks ; on prend le texte
            content_parts = [
                block.text for block in response.content if block.type == "text"
            ]
            content = "\n".join(content_parts)

            in_tokens = response.usage.input_tokens
            out_tokens = response.usage.output_tokens
            in_price, out_price = PRICING.get(self.model, (0, 0))
            cost = in_tokens * in_price + out_tokens * out_price

            return GenerationResult(
                llm_name=self.name,
                prompt_name="",
                function_id="",
                run_id=0,
                test_code=clean_code_fences(content),
                tokens_in=in_tokens,
                tokens_out=out_tokens,
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
