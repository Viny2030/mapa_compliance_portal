"""
motor_score.py
Calcula el score de compliance desde datos reales del programa.
Pesos y umbrales alineados con Ley 27.401 y guías OA (Oficina Anticorrupción).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ── Pesos por eje (deben sumar 100) ────────────────────────────────────────
PESOS = {
    "programa":       25,   # Elementos del programa de integridad
    "capacitacion":   20,   # Porcentaje de personal capacitado
    "due_diligence":  20,   # Cobertura de terceros evaluados
    "riesgo":         15,   # Mapa de riesgos actualizado
    "comunicacion":   10,   # Canales de denuncia operativos
    "investigacion":  10,   # Procedimiento de investigación interna
}

# ── Niveles de madurez OA ──────────────────────────────────────────────────
NIVELES = [
    (0,  40,   "Inicial",        "#dc2626"),
    (40, 65,   "En desarrollo",  "#f59e0b"),
    (65, 80,   "Intermedio",     "#3b82f6"),
    (80, 100.1,"Avanzado",       "#16a34a"),
]


@dataclass
class DatosPrograma:
    """Datos de entrada para el cálculo del score."""
    # Programa (0-100 cada elemento)
    codigo_conducta:         float = 0.0
    politicas_aprobadas:     float = 0.0
    canal_denuncia:          float = 0.0
    responsable_designado:   float = 0.0
    comite_compliance:       float = 0.0

    # Capacitación
    pct_personal_capacitado: float = 0.0   # 0-100
    modulos_completados:     int   = 0
    modulos_totales:         int   = 6

    # Due Diligence
    proveedores_evaluados:   int   = 0
    proveedores_totales:     int   = 1     # evitar div/0

    # Riesgo
    mapa_riesgo_actualizado: bool  = False
    meses_desde_actualizacion: int = 99

    # Comunicación
    canal_operativo:         bool  = False
    denuncias_gestionadas:   bool  = False

    # Investigación
    procedimiento_escrito:   bool  = False
    investigaciones_abiertas: int  = 0

    # Metadata
    extra: dict[str, Any] = field(default_factory=dict)


def _score_programa(d: DatosPrograma) -> float:
    elementos = [
        d.codigo_conducta,
        d.politicas_aprobadas,
        d.canal_denuncia,
        d.responsable_designado,
        d.comite_compliance,
    ]
    return sum(elementos) / len(elementos)


def _score_capacitacion(d: DatosPrograma) -> float:
    pct = d.pct_personal_capacitado
    modulos = (d.modulos_completados / max(d.modulos_totales, 1)) * 100
    return (pct * 0.6 + modulos * 0.4)


def _score_due_diligence(d: DatosPrograma) -> float:
    cobertura = (d.proveedores_evaluados / max(d.proveedores_totales, 1)) * 100
    return min(cobertura, 100)


def _score_riesgo(d: DatosPrograma) -> float:
    if not d.mapa_riesgo_actualizado:
        return 0.0
    # Penalización progresiva por antigüedad (máx 12 meses)
    penalizacion = min(d.meses_desde_actualizacion / 12, 1) * 40
    return max(100 - penalizacion, 0)


def _score_comunicacion(d: DatosPrograma) -> float:
    score = 0.0
    if d.canal_operativo:
        score += 60
    if d.denuncias_gestionadas:
        score += 40
    return score


def _score_investigacion(d: DatosPrograma) -> float:
    score = 0.0
    if d.procedimiento_escrito:
        score += 70
    # Investigaciones abiertas sin cerrar penalizan
    penalizacion = min(d.investigaciones_abiertas * 10, 30)
    score = max(score - penalizacion, 0)
    if d.procedimiento_escrito:
        score += 30
    return min(score, 100)


def calcular_score(d: DatosPrograma) -> dict:
    """
    Retorna dict con score global, score por eje, nivel y color.
    """
    ejes = {
        "programa":      _score_programa(d),
        "capacitacion":  _score_capacitacion(d),
        "due_diligence": _score_due_diligence(d),
        "riesgo":        _score_riesgo(d),
        "comunicacion":  _score_comunicacion(d),
        "investigacion": _score_investigacion(d),
    }

    score_global = sum(
        ejes[eje] * (PESOS[eje] / 100) for eje in ejes
    )
    score_global = round(score_global, 1)

    nivel = "Inicial"
    color = "#dc2626"
    for minimo, maximo, nombre, clr in NIVELES:
        if minimo <= score_global < maximo:
            nivel = nombre
            color = clr
            break

    return {
        "score_global": score_global,
        "nivel": nivel,
        "color": color,
        "ejes": {k: round(v, 1) for k, v in ejes.items()},
        "pesos": PESOS,
    }


def score_desde_dict(data: dict) -> dict:
    """Wrapper para llamar desde la API con un dict JSON."""
    d = DatosPrograma(**{k: v for k, v in data.items() if k in DatosPrograma.__dataclass_fields__})
    return calcular_score(d)
