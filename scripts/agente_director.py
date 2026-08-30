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
import re
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
        "description": (
            "[SIMULADO — no es una consulta real a AFIP todavía] Devuelve un estado de CUIT "
            "(activo/inactivo, tipo societario) calculado con una heurística de ejemplo, "
            "pendiente de reemplazo por WS_SR_PADRON_A5."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"cuit": {"type": "string", "description": "CUIT sin guiones, 11 dígitos"}},
            "required": ["cuit"],
        },
    },
    {
        "name": "consultar_uif",
        "description": (
            "[SIMULADO — no es una consulta real a la UIF todavía] Devuelve una marca de "
            "sospechoso/PEP calculada con una heurística de ejemplo sobre el CUIT, pendiente "
            "de reemplazo por la integración real con la Unidad de Información Financiera."
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
            "[SIMULADO — no es una consulta real a listas de la OCDE todavía] Devuelve una marca "
            "de lista negra/gris calculada con una heurística de ejemplo sobre el CUIT, pendiente "
            "de reemplazo por la integración real con listas de riesgo OCDE."
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

IMPORTANTE: las tres tools son simulaciones de ejemplo (ver su descripción) — todavía no consultan AFIP, \
la UIF ni la OCDE reales. Redactá los "hallazgos" y la "justificacion" dejando en claro que se trata de \
un resultado preliminar/simulado (por ejemplo: "según la fuente simulada de AFIP...", "de confirmarse con \
la fuente real..."), nunca como si fuera una verificación oficial ya realizada.

Cuando ya tengas información suficiente, tu ÚNICA respuesta debe ser el JSON de abajo. No agregues \
ninguna frase antes o después (nada de "acá está el veredicto", "con la información obtenida", etc.), \
ni backticks: el mensaje completo tiene que ser el JSON, nada más.
{
  "cuit": "...",
  "riesgo": "bajo|medio|alto",
  "hallazgos": ["..."],
  "fuentes_consultadas": ["afip", "uif", "ocde"],
  "justificacion": "una o dos oraciones explicando el veredicto, dejando en claro que las fuentes son simuladas"
}"""


# Aviso fijo que acompaña TODO veredicto de due diligence mientras las tools
# de AFIP/UIF/OCDE sigan siendo stubs (ver docstring del módulo). Se agrega
# server-side —no depende de que el modelo se acuerde de mencionarlo— para
# que ningún consumidor de la API (la UI, un script, un tercero) pueda
# tomar el veredicto como una verificación real por accidente.
AVISO_FUENTES_SIMULADAS = (
    "Resultado simulado (MVP): las consultas a AFIP/UIF/OCDE todavía son "
    "placeholders derivados del propio CUIT, no integraciones reales. "
    "No usar este veredicto para decisiones de negocio hasta reemplazar "
    "las tools por las integraciones oficiales."
)


def _marcar_simulado(resultado: dict) -> dict:
    """Agrega el flag y aviso de fuentes simuladas a cualquier veredicto de due diligence."""
    resultado["fuentes_reales"] = False
    resultado["aviso"] = AVISO_FUENTES_SIMULADAS
    return resultado


def _fallback_determinista(cuit: str) -> dict:
    """Mismo criterio que el _verificar_cuit original, para cuando no hay API key o el agente falla."""
    afip = _consultar_afip(cuit)
    uif = _consultar_uif(cuit)
    ocde = _consultar_ocde(cuit)
    riesgo = (
        "alto" if (uif["persona_expuesta_politicamente"] or ocde["lista_gris"] or ocde["lista_negra"])
        else ("bajo" if afip["valido"] else "medio")
    )
    return _marcar_simulado({
        "cuit": cuit,
        "riesgo": riesgo,
        "hallazgos": [],
        "fuentes_consultadas": ["afip", "uif", "ocde"],
        "justificacion": "Evaluación determinística (agente IA no disponible o sin ANTHROPIC_API_KEY configurada).",
    })


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
                    resultado = None
                    try:
                        resultado = json.loads(texto)
                    except json.JSONDecodeError:
                        # El modelo a veces antepone una frase antes del JSON pese a la
                        # instrucción del system prompt (ej. "Con la información obtenida,
                        # emito el veredicto final: {...}") — extraer el bloque {...} y
                        # reintentar antes de rendirse.
                        match = re.search(r"\{.*\}", texto, re.DOTALL)
                        if match:
                            try:
                                resultado = json.loads(match.group(0))
                            except json.JSONDecodeError:
                                resultado = None
                    if resultado is None:
                        log.warning(f"Respuesta final del agente no es JSON válido: {texto[:300]}")
                        resultado = _fallback_determinista(cuit)
                    else:
                        resultado = _marcar_simulado(resultado)
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
