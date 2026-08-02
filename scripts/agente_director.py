"""
agente_director.py
Agente director para due diligence de terceros: usa Claude (tool_use) para
decidir dinámicamente qué fuentes consultar (AFIP, UIF, OCDE) y en qué orden,
en vez del pipeline fijo que había antes en _verificar_cuit().

Si no hay ANTHROPIC_API_KEY configurada, o el agente falla, cae al criterio
determinístico anterior sin romper el flujo — mismo principio defensivo que
ya usa ia_alertas.py en este mismo proyecto.

Cada tool_call / tool_result / respuesta final queda persistido en
data/agente_trazabilidad.db — es el requisito de trazabilidad de un producto
de compliance: tiene que poder auditarse qué consultó el agente y por qué
llegó a ese veredicto.

Tools de hoy (AFIP/UIF/OCDE) son stubs con la misma lógica de ejemplo que
tenía _verificar_cuit(). Reemplazar por integraciones reales cuando estén
disponibles:
  AFIP → WS_SR_PADRON_A5
  UIF  → listas de personas expuestas políticamente / sospechosos reportados
  OCDE → lista de riesgo / paraísos fiscales
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx

log = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
MAX_PASOS = 6  # tope de vueltas del loop — limita costo y evita loops infinitos

API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DB_PATH = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "data"))) / "agente_trazabilidad.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pasos_agente (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sesion_id   TEXT NOT NULL,
            cuit        TEXT,
            paso        INTEGER NOT NULL,
            tipo        TEXT NOT NULL,   -- 'tool_call' | 'tool_result' | 'respuesta_final' | 'fallback'
            tool_name   TEXT,
            contenido   TEXT,            -- JSON serializado
            timestamp   TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


def _log_paso(sesion_id: str, cuit: str, paso: int, tipo: str, tool_name: Optional[str], contenido: Any) -> None:
    try:
        conn = _conn()
        conn.execute(
            "INSERT INTO pasos_agente (sesion_id, cuit, paso, tipo, tool_name, contenido, timestamp) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                sesion_id, cuit, paso, tipo, tool_name,
                json.dumps(contenido, ensure_ascii=False, default=str),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.warning(f"No se pudo loguear paso de trazabilidad: {e}")


# ── Tools disponibles para el agente (stubs — ver docstring del módulo) ──────

def _consultar_afip(cuit: str) -> dict:
    valido = len(cuit) == 11
    return {
        "cuit": cuit,
        "valido": valido,
        "estado": "ACTIVO" if valido else "NO ENCONTRADO",
        "tipo_societario": "Sociedad Anónima" if valido else None,
    }


def _consultar_uif(cuit: str) -> dict:
    digito = int(cuit[-1]) if cuit and cuit[-1].isdigit() else 0
    return {
        "cuit": cuit,
        "lista_sospechosos": False,
        "persona_expuesta_politicamente": digito == 7,  # placeholder, no es dato real
    }


def _consultar_ocde(cuit: str) -> dict:
    digito = int(cuit[-1]) if cuit and cuit[-1].isdigit() else 0
    return {
        "cuit": cuit,
        "lista_negra": False,
        "lista_gris": digito % 3 == 0,  # placeholder, no es dato real
    }


TOOLS_PYTHON = {
    "consultar_afip": _consultar_afip,
    "consultar_uif": _consultar_uif,
    "consultar_ocde": _consultar_ocde,
}

TOOLS_SCHEMA = [
    {
        "name": "consultar_afip",
        "description": "Consulta el padrón de AFIP para verificar el estado de una CUIT (activo/inactivo, tipo societario).",
        "input_schema": {
            "type": "object",
            "properties": {"cuit": {"type": "string", "description": "CUIT sin guiones, 11 dígitos"}},
            "required": ["cuit"],
        },
    },
    {
        "name": "consultar_uif",
        "description": (
            "Consulta a la UIF (Unidad de Información Financiera) si el titular de la CUIT figura en "
            "listas de sospechosos o es una persona expuesta políticamente (PEP)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"cuit": {"type": "string", "description": "CUIT sin guiones, 11 dígitos"}},
            "required": ["cuit"],
        },
    },
    {
        "name": "consultar_ocde",
        "description": (
            "Consulta listas de riesgo de la OCDE (lista negra/gris de jurisdicciones o entidades "
            "sancionadas) asociadas a la CUIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"cuit": {"type": "string", "description": "CUIT sin guiones, 11 dígitos"}},
            "required": ["cuit"],
        },
    },
]

SYSTEM_PROMPT = """Sos el agente de due diligence de terceros de un sistema de compliance (Ley 27.401, Argentina).
Tu tarea: dado un CUIT, decidir qué fuentes consultar (afip, uif, ocde — podés llamar las que necesites, \
en el orden que corresponda, y no repetir una fuente ya consultada) y devolver un veredicto final.

Cuando ya tengas información suficiente, respondé en texto plano (sin más tool calls) con un JSON único \
y exacto, sin texto adicional ni backticks:
{
  "cuit": "...",
  "riesgo": "bajo|medio|alto",
  "hallazgos": ["..."],
  "fuentes_consultadas": ["afip", "uif", "ocde"],
  "justificacion": "una o dos oraciones explicando el veredicto"
}"""


def _fallback_determinista(cuit: str) -> dict:
    """Mismo criterio que el _verificar_cuit original, para cuando no hay API key o el agente falla."""
    afip = _consultar_afip(cuit)
    uif = _consultar_uif(cuit)
    ocde = _consultar_ocde(cuit)
    riesgo = (
        "alto" if (uif["persona_expuesta_politicamente"] or ocde["lista_gris"] or ocde["lista_negra"])
        else ("bajo" if afip["valido"] else "medio")
    )
    return {
        "cuit": cuit,
        "riesgo": riesgo,
        "hallazgos": [],
        "fuentes_consultadas": ["afip", "uif", "ocde"],
        "justificacion": "Evaluación determinística (agente IA no disponible o sin ANTHROPIC_API_KEY configurada).",
    }


async def ejecutar_due_diligence_async(cuit: str) -> dict:
    """
    Corre el agente director sobre un CUIT y devuelve el veredicto final.
    Loguea cada tool_call/tool_result/respuesta en agente_trazabilidad.db.
    Si no hay API key, si el agente excede MAX_PASOS, o si falla, cae al
    criterio determinístico sin romper el flujo.
    """
    sesion_id = str(uuid.uuid4())

    if not API_KEY:
        resultado = _fallback_determinista(cuit)
        _log_paso(sesion_id, cuit, 0, "fallback", None, resultado)
        return resultado

    messages: list[dict] = [{
        "role": "user",
        "content": f"Investigá la CUIT {cuit} y devolvé el veredicto de riesgo.",
    }]

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            for paso in range(1, MAX_PASOS + 1):
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
                        "tools": TOOLS_SCHEMA,
                        "messages": messages,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                stop_reason = data.get("stop_reason")
                content_blocks = data.get("content", [])

                messages.append({"role": "assistant", "content": content_blocks})

                if stop_reason != "tool_use":
                    texto = "".join(
                        b.get("text", "") for b in content_blocks if b.get("type") == "text"
                    ).strip()
                    texto = texto.replace("```json", "").replace("```", "").strip()
                    try:
                        resultado = json.loads(texto)
                    except json.JSONDecodeError:
                        log.warning(f"Respuesta final del agente no es JSON válido: {texto[:200]}")
                        resultado = _fallback_determinista(cuit)
                    _log_paso(sesion_id, cuit, paso, "respuesta_final", None, resultado)
                    return resultado

                # stop_reason == "tool_use": ejecutar cada tool pedida y devolver el resultado
                tool_results = []
                for block in content_blocks:
                    if block.get("type") != "tool_use":
                        continue
                    tool_name = block["name"]
                    tool_input = block.get("input", {})
                    _log_paso(sesion_id, cuit, paso, "tool_call", tool_name, tool_input)

                    fn = TOOLS_PYTHON.get(tool_name)
                    if fn is None:
                        salida = {"error": f"tool desconocida: {tool_name}"}
                    else:
                        try:
                            salida = fn(**tool_input)
                        except Exception as e:
                            salida = {"error": str(e)}

                    _log_paso(sesion_id, cuit, paso, "tool_result", tool_name, salida)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": json.dumps(salida, ensure_ascii=False),
                    })

                messages.append({"role": "user", "content": tool_results})

        log.warning(f"Agente de due diligence excedió MAX_PASOS para CUIT {cuit}")
        resultado = _fallback_determinista(cuit)
        _log_paso(sesion_id, cuit, MAX_PASOS, "fallback", None, resultado)
        return resultado

    except Exception as e:
        log.warning(f"Error corriendo agente de due diligence para {cuit}: {e}")
        resultado = _fallback_determinista(cuit)
        _log_paso(sesion_id, cuit, 0, "fallback", None, resultado)
        return resultado


def historial(cuit: Optional[str] = None, limit: int = 100) -> list[dict]:
    """Devuelve el historial de trazabilidad, opcionalmente filtrado por CUIT (más reciente primero)."""
    conn = _conn()
    if cuit:
        rows = conn.execute(
            "SELECT * FROM pasos_agente WHERE cuit = ? ORDER BY id DESC LIMIT ?", (cuit, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM pasos_agente ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
