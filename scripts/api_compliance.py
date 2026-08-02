"""
api_compliance.py
Endpoints REST del Monitor de Compliance.
"""
from __future__ import annotations
import json
import re
from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form, Header, Request
from fastapi.responses import Response
from pathlib import Path
from pydantic import BaseModel

from scripts.motor_score import score_desde_dict, calcular_score, DatosPrograma, PESOS, score_lei_12846_desde_dict, calcular_score_lei_12846, DadosLei12846, ELEMENTOS_LEI_12846
from scripts.etl_alertas import cargar_alertas, ALERTAS_FILE
from scripts.etl_normativa import cargar_normativa
from scripts.generador_pdf import generar_reporte
from scripts.ia_alertas import resumir_alerta_async
from scripts.procesador_docs import (
    procesar_documento, guardar_documento,
    registrar_documento, listar_documentos, eliminar_documento,
    TIPOS_DOC,
)
from scripts.canal_denuncias import _validar_token
from scripts.rate_limit import limitar

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
async def calcular_score_endpoint(req: ScoreRequest, request: Request):
    """Calcula el score a partir de los datos reales del programa."""
    limitar(request, "score", max_llamadas=30, ventana_seg=60)
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


@router.get("/alertas/{alerta_id}/resumen")
async def resumen_ia_alerta(alerta_id: str):
    """
    Genera (o devuelve cacheado) el resumen IA de una alerta específica.
    Si el resumen ya existe en el JSON lo devuelve directo.
    Si no, llama a Claude API on-demand y lo persiste.
    """
    data = cargar_alertas()
    alertas = data.get("alertas", [])
    alerta = next((a for a in alertas if a.get("id") == alerta_id), None)

    if not alerta:
        raise HTTPException(status_code=404, detail=f"Alerta '{alerta_id}' no encontrada")

    # Devolver caché si ya existe
    if alerta.get("resumen_ia"):
        return {"id": alerta_id, "resumen_ia": alerta["resumen_ia"], "cached": True}

    # Generar on-demand
    resumen = await resumir_alerta_async(alerta)
    if not resumen:
        raise HTTPException(
            status_code=503,
            detail="Resumen IA no disponible. Verificar ANTHROPIC_API_KEY en variables de entorno."
        )

    # Persistir en el JSON para no volver a llamar
    # Usa ALERTAS_FILE de etl_alertas.py (respeta DATA_DIR) en vez de un
    # path hardcodeado, para no desincronizarse si DATA_DIR cambia.
    alerta["resumen_ia"] = resumen
    if ALERTAS_FILE.exists():
        ALERTAS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    return {"id": alerta_id, "resumen_ia": resumen, "cached": False}


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
async def due_diligence(req: DueDiligenceRequest, request: Request):
    """Verificación de CUIT contra AFIP, UIF y listas OCDE."""
    limitar(request, "due-diligence", max_llamadas=20, ventana_seg=60)
    cuit = _limpiar_cuit(req.cuit)
    if not cuit:
        raise HTTPException(status_code=400, detail="CUIT inválido")
    return _verificar_cuit(cuit)


@router.post("/due-diligence/agente")
async def due_diligence_agente(req: DueDiligenceRequest, request: Request):
    """
    Due diligence vía agente director (Claude tool_use): decide dinámicamente
    qué fuentes consultar (AFIP/UIF/OCDE) según el caso, en vez de llamarlas
    siempre en el mismo orden fijo. Trazabilidad completa en agente_trazabilidad.db.
    Sin ANTHROPIC_API_KEY configurada, cae al criterio determinístico anterior.
    """
    limitar(request, "due-diligence-agente", max_llamadas=10, ventana_seg=60)
    from scripts.agente_director import ejecutar_due_diligence_async
    cuit = _limpiar_cuit(req.cuit)
    if not cuit:
        raise HTTPException(status_code=400, detail="CUIT inválido")
    return await ejecutar_due_diligence_async(cuit)


@router.get("/due-diligence/agente/historial")
async def due_diligence_agente_historial(request: Request, cuit: Optional[str] = Query(None)):
    """Trazabilidad de corridas del agente de due diligence (más reciente primero)."""
    limitar(request, "due-diligence-agente-historial", max_llamadas=30, ventana_seg=60)
    from scripts.agente_director import historial
    cuit_limpio = _limpiar_cuit(cuit) if cuit else None
    return {"historial": historial(cuit_limpio)}


@router.post("/reporte/pdf")
async def exportar_pdf(req: PDFRequest, request: Request):
    """Genera y retorna el reporte PDF ejecutivo."""
    limitar(request, "reporte-pdf", max_llamadas=10, ventana_seg=60)
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


# ── Portal multi-cliente (portal.html) ──────────────────────────────────────

@router.get("/clientes")
async def get_clientes(x_session_token: str = Header(...)):
    """
    Lista los clientes registrados en data/clientes.json, para el portal
    multi-cliente (portal.html). Nunca devuelve password_hash ni otros
    campos sensibles — data/clientes.json está marcado "NO exponer
    públicamente" y este endpoint filtra antes de responder.

    Requiere sesión (X-Session-Token) — nombre, CUIT y email de los
    clientes son datos reales, no deben quedar accesibles a cualquiera
    con la URL.
    """
    _validar_token(x_session_token)
    clientes_file = Path(__file__).parent.parent / "data" / "clientes.json"
    if not clientes_file.exists():
        return {"clientes": []}

    try:
        data = json.loads(clientes_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="data/clientes.json inválido")

    clientes_publicos = []
    for c in data.get("clientes", []):
        c = dict(c)
        c.pop("password_hash", None)  # nunca exponer el hash de contraseña
        c.setdefault("onboarding", None)
        c.setdefault("modulos_activos", {})
        clientes_publicos.append(c)

    return {"clientes": clientes_publicos}


# ── Endpoints de carga de documentos ────────────────────────────────────────

@router.get("/documentos-cliente")
async def get_documentos_cliente():
    """Lista todos los documentos subidos con su metadata."""
    docs = listar_documentos()
    elementos_cubiertos = {d["elemento_compliance"] for d in docs if d.get("elemento_compliance")}
    total_tipos = len(TIPOS_DOC)
    return {
        "total": len(docs),
        "completitud_pct": round(len(elementos_cubiertos) / total_tipos * 100) if total_tipos else 0,
        "elementos_cubiertos": list(elementos_cubiertos),
        "documentos": docs,
    }


@router.get("/documentos-cliente/tipos")
async def get_tipos_documentos():
    """Devuelve los tipos de documento reconocidos por el sistema."""
    return {
        "tipos": [
            {"id": k, "label": v["label"], "icono": v["icono"], "elemento": v["elemento"]}
            for k, v in TIPOS_DOC.items()
        ]
    }


@router.get("/documentos-cliente/checklist")
async def checklist_documentacion():
    """Devuelve qué documentos están cubiertos y cuáles faltan."""
    docs = listar_documentos()
    elementos_subidos = {}
    for d in docs:
        elem = d.get("elemento_compliance", "")
        if elem and elem not in elementos_subidos:
            elementos_subidos[elem] = {
                "archivo": d["nombre_archivo"],
                "fecha": d.get("fecha_detectada"),
                "subido_en": d.get("subido_en"),
            }

    checklist = []
    for tipo_id, meta in TIPOS_DOC.items():
        elem = meta.get("elemento", "")
        cubierto = elem in elementos_subidos
        checklist.append({
            "tipo": tipo_id,
            "label": meta["label"],
            "icono": meta["icono"],
            "elemento_compliance": elem,
            "cubierto": cubierto,
            "archivo": elementos_subidos.get(elem, {}).get("archivo"),
            "fecha": elementos_subidos.get(elem, {}).get("fecha"),
        })

    cubiertos = sum(1 for c in checklist if c["cubierto"])
    return {
        "cubiertos": cubiertos,
        "total": len(checklist),
        "pct": round(cubiertos / len(checklist) * 100) if checklist else 0,
        "checklist": checklist,
    }


@router.post("/documentos-cliente/upload")
async def upload_documento(
    request: Request,
    archivo: UploadFile = File(...),
    tipo_forzado: str = Form(""),
    x_session_token: str = Header(...),
):
    """
    Sube un documento y lo procesa. Formatos: PDF, XLSX, XLS, CSV, DOC, DOCX.
    Requiere sesión (X-Session-Token).
    """
    _validar_token(x_session_token)
    limitar(request, "documentos-upload", max_llamadas=10, ventana_seg=60)

    EXTENSIONES_OK = {".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx"}
    MAX_MB = 20

    ext = Path(archivo.filename).suffix.lower()
    if ext not in EXTENSIONES_OK:
        raise HTTPException(
            status_code=415,
            detail=f"Formato no soportado: {ext}. Usar: {', '.join(EXTENSIONES_OK)}"
        )

    contenido = await archivo.read()
    if len(contenido) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Archivo mayor a {MAX_MB} MB")

    metadata = procesar_documento(contenido, archivo.filename, tipo_forzado)
    try:
        guardar_documento(contenido, archivo.filename, metadata["tipo"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    registrar_documento(metadata)

    return {
        "ok": True,
        "mensaje": f"'{archivo.filename}' subido correctamente",
        "metadata": metadata,
    }


@router.delete("/documentos-cliente/{tipo}/{nombre_archivo}")
async def delete_documento(tipo: str, nombre_archivo: str, x_session_token: str = Header(...)):
    """Elimina un documento del registro y del disco. Requiere sesión (X-Session-Token)."""
    _validar_token(x_session_token)
    try:
        eliminar_documento(nombre_archivo, tipo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "mensaje": f"'{nombre_archivo}' eliminado"}


# ── Lei Anticorrupção 12.846/2013 — Brasil ───────────────────────────────────

class Lei12846Request(BaseModel):
    programa_integridade:    float = 0
    codigo_conduta:          float = 0
    responsavel_compliance:  float = 0
    treinamentos:            float = 0
    canal_denuncia:          float = 0
    due_diligence_terceiros: float = 0
    acordo_leniencia:        float = 0
    auditoria_interna:       float = 0
    controles_contabeis:     float = 0
    politica_doacoes:        float = 0
    monitoramento:           float = 0


@router.get("/brasil/score/demo")
async def score_brasil_demo():
    """Score demo para Lei Anticorrupção 12.846/2013."""
    d = DadosLei12846(
        programa_integridade=70, codigo_conduta=85,
        responsavel_compliance=100, treinamentos=60,
        canal_denuncia=80, due_diligence_terceiros=45,
        acordo_leniencia=30, auditoria_interna=50,
        controles_contabeis=75, politica_doacoes=20,
        monitoramento=40,
    )
    return calcular_score_lei_12846(d)


@router.post("/brasil/score")
async def score_brasil(req: Lei12846Request):
    """Calcula el score de la Lei Anticorrupção 12.846/2013."""
    try:
        return score_lei_12846_desde_dict(req.dict())
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/brasil/elementos")
async def elementos_brasil():
    """Lista los elementos del programa de integridad según Lei 12.846."""
    return {"elementos": ELEMENTOS_LEI_12846}
