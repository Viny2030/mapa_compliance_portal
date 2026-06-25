"""
ia_alertas.py
Genera resúmenes en lenguaje simple de alertas regulatorias usando Claude API.
Se llama desde etl_alertas.py (batch) y desde api_compliance.py (on-demand).

El resumen responde siempre a 3 preguntas concretas para el compliance officer:
  1. ¿Qué cambió o vence?
  2. ¿A quién afecta en la empresa?
  3. ¿Qué acción concreta hay que tomar?

Sin API key configurada, devuelve None silenciosamente (no rompe el flujo).
"""
from __future__ import annotations
import json
import logging
import os
from typing import Optional

import httpx

log = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 300

# La API key se lee desde env — nunca hardcodeada
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Sos un asistente de compliance empresarial para Latinoamérica y España.
Tu tarea es leer alertas regulatorias y resumirlas en lenguaje claro para un compliance officer de una PYME.

Respondé SIEMPRE en este formato JSON exacto, sin texto adicional:
{
  "que_cambio": "Una oración corta explicando qué cambió o qué vence.",
  "a_quien_afecta": "Qué área o rol de la empresa debe actuar (Finanzas, RRHH, Directorio, etc.).",
  "accion_concreta": "La acción específica que hay que tomar, con verbo en infinitivo.",
  "urgencia": "alta|media|baja"
}"""


def _build_user_prompt(alerta: dict) -> str:
    partes = [
        f"Fuente: {alerta.get('fuente', 'Desconocida')}",
        f"Categoría: {alerta.get('categoria', '')}",
        f"Descripción: {alerta.get('descripcion', '')}",
    ]
    if alerta.get("vencimiento"):
        partes.append(f"Vencimiento: {alerta['vencimiento']}")
    if alerta.get("severidad"):
        partes.append(f"Severidad: {alerta['severidad']}")
    return "\n".join(partes)


def resumir_alerta(alerta: dict) -> Optional[dict]:
    """
    Llama a Claude API y devuelve un dict con el resumen estructurado.
    Devuelve None si no hay API key o si hay error.
    """
    if not API_KEY:
        log.debug("ANTHROPIC_API_KEY no configurada — resumen IA omitido")
        return None

    prompt = _build_user_prompt(alerta)

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": MODEL,
                    "max_tokens": MAX_TOKENS,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            texto = data["content"][0]["text"].strip()
            # Limpiar posibles backticks de markdown
            texto = texto.replace("```json", "").replace("```", "").strip()
            return json.loads(texto)
    except json.JSONDecodeError as e:
        log.warning(f"Respuesta IA no es JSON válido para alerta {alerta.get('id')}: {e}")
        return None
    except Exception as e:
        log.warning(f"Error llamando API para alerta {alerta.get('id')}: {e}")
        return None


async def resumir_alerta_async(alerta: dict) -> Optional[dict]:
    """
    Versión async para usar desde FastAPI (on-demand, sin bloquear el event loop).
    """
    if not API_KEY:
        return None

    prompt = _build_user_prompt(alerta)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": MODEL,
                    "max_tokens": MAX_TOKENS,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            texto = data["content"][0]["text"].strip()
            texto = texto.replace("```json", "").replace("```", "").strip()
            return json.loads(texto)
    except Exception as e:
        log.warning(f"Error async llamando API para alerta {alerta.get('id')}: {e}")
        return None
