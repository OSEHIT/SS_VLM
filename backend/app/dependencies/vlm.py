"""Dependency injection pour le modèle VLM Qwen2-VL-2B.

Chargement via Lifespan Event (Option A validée par l'utilisateur).
Le modèle est chargé une seule fois au démarrage et partagé entre toutes les requêtes.
"""

from dataclasses import dataclass, field
from typing import Any

from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

from app.config import get_settings


@dataclass
class VLMContainer:
    """Container pour le modèle VLM et son processeur."""

    model: Any = field(default=None)
    processor: Any = field(default=None)
    _loaded: bool = field(default=False)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        """Charge le modèle et le processeur en mémoire."""
        if self._loaded:
            return

        settings = get_settings()
        model_id = settings.vlm_model_id
        device = settings.vlm_device

        print(f"[VLM] Chargement du modèle {model_id} sur {device}...")

        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map=device if device != "cpu" else None,
        )

        if device == "cpu":
            self.model = self.model.float()

        self.model.eval()
        self._loaded = True
        print(f"[VLM] Modèle chargé avec succès sur {device}.")

    def unload(self) -> None:
        """Libère le modèle de la mémoire."""
        self.model = None
        self.processor = None
        self._loaded = False
        print("[VLM] Modèle déchargé.")


# Singleton global — initialisé dans le lifespan de FastAPI
vlm_container = VLMContainer()


def get_vlm() -> VLMContainer:
    """Dependency FastAPI pour injecter le VLM dans les routes."""
    if not vlm_container.is_loaded:
        raise RuntimeError("VLM non chargé. Vérifiez le lifespan de l'app.")
    return vlm_container
