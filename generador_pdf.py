"""
generador_pdf.py
Genera el reporte PDF ejecutivo de compliance.
Requiere: reportlab
"""
from __future__ import annotations
import io
from datetime import date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

# ── Paleta ─────────────────────────────────────────────────────────────────
AZUL    = colors.HexColor("#1a3a5c")
VERDE   = colors.HexColor("#16a34a")
NARANJA = colors.HexColor("#f59e0b")
ROJO    = colors.HexColor("#dc2626")
GRIS    = colors.HexColor("#f1f5f9")
BLANCO  = colors.white


def _color_severidad(sev: str):
    return {"rojo": ROJO, "naranja": NARANJA, "verde": VERDE}.get(sev, GRIS)


def _color_score(score: float):
    if score >= 80: return VERDE
    if score >= 65: return colors.HexColor("#3b82f6")
    if score >= 40: return NARANJA
    return ROJO


def generar_reporte(datos: dict[str, Any]) -> bytes:
    """
    Genera el PDF y retorna los bytes.
    `datos` debe contener: empresa, score, nivel, ejes, alertas, plan_mejora.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title=f"Reporte Compliance — {datos.get('empresa', 'Empresa')}",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=AZUL, fontSize=16, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=AZUL, fontSize=12, spaceAfter=2)
    normal = styles["Normal"]
    small = ParagraphStyle("small", parent=normal, fontSize=8, textColor=colors.HexColor("#555"))

    story = []

    # ── Portada ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("REPORTE EJECUTIVO DE COMPLIANCE", h1))
    story.append(Paragraph(f"Programa de Integridad · Ley 27.401", h2))
    story.append(HRFlowable(width="100%", thickness=2, color=AZUL))
    story.append(Spacer(1, 0.3*cm))

    empresa = datos.get("empresa", "—")
    story.append(Paragraph(f"<b>Empresa:</b> {empresa}", normal))
    story.append(Paragraph(f"<b>Fecha:</b> {date.today().strftime('%d/%m/%Y')}", normal))
    story.append(Spacer(1, 0.5*cm))

    # ── Score global ────────────────────────────────────────────────────────
    score = datos.get("score", 0)
    nivel = datos.get("nivel", "—")
    color_sc = _color_score(score)

    score_data = [
        ["Score Global", "Nivel de Madurez"],
        [f"{score}/100", nivel],
    ]
    score_table = Table(score_data, colWidths=[8*cm, 8*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
        ("BACKGROUND", (0, 1), (0, 1), color_sc),
        ("TEXTCOLOR",  (0, 1), (0, 1), BLANCO),
        ("FONTSIZE",   (0, 1), (-1, 1), 22),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",   (0, 1), (-1, 1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [None]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Scores por eje ──────────────────────────────────────────────────────
    story.append(Paragraph("Score por Eje", h2))
    ejes = datos.get("ejes", {})
    nombres_ejes = {
        "programa": "Programa de Integridad",
        "capacitacion": "Capacitación",
        "due_diligence": "Due Diligence",
        "riesgo": "Mapa de Riesgo",
        "comunicacion": "Comunicación / Denuncias",
        "investigacion": "Investigación Interna",
    }
    eje_data = [["Eje", "Score", "Estado"]]
    for clave, nombre in nombres_ejes.items():
        val = ejes.get(clave, 0)
        estado = "✓ OK" if val >= 65 else ("⚠ Mejora" if val >= 40 else "✗ Crítico")
        eje_data.append([nombre, f"{val:.0f}/100", estado])

    eje_table = Table(eje_data, colWidths=[9*cm, 3*cm, 4*cm])
    eje_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRIS, BLANCO]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(eje_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Alertas ─────────────────────────────────────────────────────────────
    alertas = datos.get("alertas", [])
    if alertas:
        story.append(Paragraph("Alertas Activas", h2))
        al_data = [["Severidad", "Descripción", "Vencimiento"]]
        for a in alertas[:10]:
            al_data.append([
                a.get("severidad", "—").upper(),
                a.get("descripcion", "—")[:70],
                a.get("vencimiento") or "—",
            ])
        al_table = Table(al_data, colWidths=[2.5*cm, 11*cm, 3*cm])
        al_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRIS, BLANCO]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(al_table)
        story.append(Spacer(1, 0.5*cm))

    # ── Plan de mejora ──────────────────────────────────────────────────────
    plan = datos.get("plan_mejora", [])
    if plan:
        story.append(PageBreak())
        story.append(Paragraph("Plan de Mejora Priorizado", h2))
        plan_data = [["#", "Acción", "Prioridad", "Responsable", "Vence", "Estado"]]
        for i, item in enumerate(plan[:10], 1):
            plan_data.append([
                str(i),
                item.get("accion", "—")[:50],
                item.get("prioridad", "—").upper(),
                item.get("responsable", "—"),
                item.get("vence", "—"),
                item.get("estado", "—"),
            ])
        plan_table = Table(plan_data, colWidths=[0.6*cm, 6.5*cm, 2*cm, 3*cm, 2.5*cm, 2.4*cm])
        plan_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), AZUL),
            ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRIS, BLANCO]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ]))
        story.append(plan_table)

    # ── Pie ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Paragraph(
        "Reporte generado por el Monitor de Compliance Empresarial · "
        "Ph.D. Vicente H. Monteverde · mapatransparencia-production.up.railway.app",
        small,
    ))

    doc.build(story)
    return buffer.getvalue()
