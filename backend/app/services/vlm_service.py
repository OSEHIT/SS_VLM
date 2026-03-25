"""Service d'inférence VLM via Qwen2-VL-2B-Instruct."""

import json
import re

from PIL import Image
from qwen_vl_utils import process_vision_info

from app.dependencies.vlm import VLMContainer
from app.core import VLMInferenceError


def run_inference(vlm: VLMContainer, image: Image.Image, prompt: str) -> dict:
    """Exécute une inférence VLM sur une image avec le prompt donné.

    Args:
        vlm: Container VLM chargé (modèle + processeur)
        image: Image PIL à analyser
        prompt: Prompt textuel pour guider l'extraction

    Returns:
        Dictionnaire parsé depuis la sortie JSON du VLM

    Raises:
        VLMInferenceError: Si l'inférence ou le parsing échoue
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    try:
        text_input = vlm.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = vlm.processor(
            text=[text_input],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(vlm.model.device)

        generated_ids = vlm.model.generate(**inputs, max_new_tokens=256)

        # Découper les tokens d'entrée pour ne garder que la génération
        generated_ids_trimmed = [
            out_ids[len(in_ids):]
            for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        raw_output = vlm.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]

    except Exception as e:
        raise VLMInferenceError(f"Erreur lors de l'inférence VLM : {e}")

    return _parse_vlm_output(raw_output)


def _parse_vlm_output(raw: str) -> dict:
    """Parse la sortie brute du VLM en dictionnaire JSON.

    Gère les cas où le VLM entoure le JSON de markdown fences.
    """
    cleaned = raw.strip()

    # Retirer les fences markdown ```json ... ```
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1)

    # Extraire le premier objet JSON
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not json_match:
        return {"raw": raw, "parse_error": True}

    try:
        return {**json.loads(json_match.group()), "raw": raw}
    except json.JSONDecodeError:
        return {"raw": raw, "parse_error": True}
