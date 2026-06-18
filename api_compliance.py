"""
api_compliance.py
Endpoints REST del Monitor de Compliance.
"""
from __future__ import annotations
import json
import re
from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from scripts.motor_score import score_desde_dict, calcular_score, DatosPrograma, PESOS
from scripts.etl_alertas import cargar_alertas
from scripts.etl_normativa import cargar_normativa
from scripts.generador_pdf import generar_reporte

router = APIRouter()


# ── Modelos Pydantic ────────────────────────────────────────────────────────

class ScoreRequest(BaseModel):
    codigo_conducta:          float = 0
    politicas_aprobadas:      float = 0
    canal_denuncia:           float = 0
    responsable_designado:    float = 0
    comite_compliance:        float = 0
    pct_personal_capacitado:  float = 0
    modulos_completados:      int   = 0
    modulos_totales:          int   = 6
    proveedores_evaluados:    int   = 0
    proveedores_totales:      int   = 1
    mapa_riesgo_actualizado:  bool  = False
    meses_desde_actualizacion: int  = 99
    canal_operativo:          bool  = False
    denuncias_gestionadas:    bool  = False
    procedimiento_escrito:    bool  = False
    investigaciones_abiertas: int   = 0


class PDFRequest(BaseModel):
    empresa:      str
    score:        float
    nivel:        str
    ejes:         dict[str, float]
    alertas:      list[dict] = []
    plan_mejora:  list[dict] = []


class DueDiligenceRequest(BaseModel):
    cuit: str


# ── Helpers ─────────────────────────────────────────────────────────────────

def _limpiar_cuit(cuit: str) -> str:
    return re.sub(r"[^0-9]", "", cuit)


def _verificar_cuit(cuit: str) -> dict:
    """
    Stub de verificación. En producción conectar a:
    - AFIP (WS_SR_PADRON_A5)
    - OCDE lista de riesgo
    - UIF personas expuestas
    """
    digito_verificador = int(cuit[-1]) if cuit else 0
    es_valido = len(cuit) == 11
    return {
        "cuit": cuit,
        "valido": es_valido,
        "afip": {"estado": "ACTIVO" if es_valido else "NO ENCONTRADO", "tipo": "Sociedad Anónima"},
        "uif": {"lista_sospechosos": False, "pep": False},
        "ocde": {"lista_negra": False, "lista_gris": False},
        "riesgo": "bajo" if es_valido and digito_verificador % 3 != 0 else "medio",
        "fecha_consulta": date.today().isoformat(),
    }


# ── Endpoints ───────────────────────────────────────────────────────────────

@router.get("/score/demo")
async def score_demo():
    """Score de demostración con datos ficticios."""
    d = DatosPrograma(
        codigo_conducta=80, politicas_aprobadas=70, canal_denuncia=100,
        responsable_designado=100, comite_compliance=60,
        pct_personal_capacitado=65, modulos_completados=4, modulos_totales=6,
        proveedores_evaluados=12, proveedores_totales=20,
        mapa_riesgo_actualizado=True, meses_desde_actualizacion=3,
        canal_operativo=True, denuncias_gestionadas=True,
        procedimiento_escrito=True, investigaciones_abiertas=1,
    )
    return calcular_score(d)


@router.post("/score")
async def calcular_score_endpoint(req: ScoreRequest):
    """Calcula el score a partir de los datos reales del programa."""
    try:
        resultado = score_desde_dict(req.dict())
        return resultado
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/alertas")
async def get_alertas(
    severidad: Optional[str] = Query(None, description="rojo|naranja|verde"),
    categoria: Optional[str] = Query(None),
):
    """Devuelve alertas activas del programa."""
    data = cargar_alertas()
    alertas = data.get("alertas", [])
    if severidad:
        alertas = [a for a in alertas if a.get("severidad") == severidad]
    if categoria:
        alertas = [a for a in alertas if a.get("categoria") == categoria]
    return {
        "actualizado": data.get("actualizado"),
        "total": len(alertas),
        "alertas": alertas,
    }


@router.get("/normativa")
async def get_normativa(
    categoria: Optional[str] = Query(None),
    pais: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Búsqueda de texto libre"),
):
    """Devuelve el catálogo de normativa con filtros opcionales."""
    data = cargar_normativa()
    normas = data.get("normativa", [])
    if categoria:
        normas = [n for n in normas if n.get("categoria") == categoria]
    if pais:
        normas = [n for n in normas if n.get("pais", "").upper() == pais.upper()]
    if q:
        q_lower = q.lower()
        normas = [n for n in normas if q_lower in (n.get("nombre","") + n.get("descripcion","")).lower()]
    return {
        "actualizado": data.get("actualizado"),
        "categorias": data.get("categorias", {}),
        "total": len(normas),
        "normativa": normas,
    }


@router.post("/due-diligence")
async def due_diligence(req: DueDiligenceRequest):
    """Verificación de CUIT contra AFIP, UIF y listas OCDE."""
    cuit = _limpiar_cuit(req.cuit)
    if not cuit:
        raise HTTPException(status_code=400, detail="CUIT inválido")
    return _verificar_cuit(cuit)


@router.post("/reporte/pdf")
async def exportar_pdf(req: PDFRequest):
    """Genera y retorna el reporte PDF ejecutivo."""
    try:
        pdf_bytes = generar_reporte(req.dict())
        nombre = f"compliance_{req.empresa.replace(' ', '_')}_{date.today()}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")


@router.get("/historial-score")
async def historial_score():
    """
    Retorna el historial de score mes a mes.
    En producción leer desde base de datos; aquí devuelve ejemplo.
    """
    return {
        "historial": [
            {"mes": "Ene 2026", "score": 42},
            {"mes": "Feb 2026", "score": 48},
            {"mes": "Mar 2026", "score": 53},
            {"mes": "Abr 2026", "score": 58},
            {"mes": "May 2026", "score": 63},
            {"mes": "Jun 2026", "score": 67},
        ]
    }


@router.get("/plan-mejora")
async def plan_mejora():
    """Plan de mejora priorizado (demo)."""
    return {
        "plan": [
            {"prioridad": "alta", "accion": "Completar módulo UIF — prevención lavado",
             "responsable": "RRHH", "vence": "2026-06-30", "estado": "en_progreso"},
            {"prioridad": "alta", "accion": "Actualizar mapa de riesgos de corrupción",
             "responsable": "Compliance Officer", "vence": "2026-07-15", "estado": "pendiente"},
            {"prioridad": "media", "accion": "Evaluar 8 proveedores pendientes Due Diligence",
             "responsable": "Compras", "vence": "2026-07-31", "estado": "pendiente"},
            {"prioridad": "media", "accion": "Renovar certificación canal de denuncias",
             "responsable": "Legal", "vence": "2026-07-03", "estado": "en_progreso"},
            {"prioridad": "baja", "accion": "Capacitar nuevos ingresos Q2",
             "responsable": "RRHH", "vence": "2026-08-31", "estado": "pendiente"},
        ]
    }
