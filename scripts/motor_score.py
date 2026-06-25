"""
motor_score.py
Calcula el score de compliance desde datos reales del programa.
Pesos y umbrales alineados con Ley 27.401 y guÃ­as OA (Oficina AnticorrupciÃ³n).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ââ Pesos por eje (deben sumar 100) ââââââââââââââââââââââââââââââââââââââââ
PESOS = {
    "programa":       25,   # Elementos del programa de integridad
    "capacitacion":   20,   # Porcentaje de personal capacitado
    "due_diligence":  20,   # Cobertura de terceros evaluados
    "riesgo":         15,   # Mapa de riesgos actualizado
    "comunicacion":   10,   # Canales de denuncia operativos
    "investigacion":  10,   # Procedimiento de investigaciÃ³n interna
}

# ââ Niveles de madurez OA ââââââââââââââââââââââââââââââââââââââââââââââââââ
NIVELES = [
    (0,  40,   "Inicial",        "#dc2626"),
    (40, 65,   "En desarrollo",  "#f59e0b"),
    (65, 80,   "Intermedio",     "#3b82f6"),
    (80, 100.1,"Avanzado",       "#16a34a"),
]


@dataclass
class DatosPrograma:
    """Datos de entrada para el cÃ¡lculo del score."""
    # Programa (0-100 cada elemento)
    codigo_conducta:         float = 0.0
    politicas_aprobadas:     float = 0.0
    canal_denuncia:          float = 0.0
    responsable_designado:   float = 0.0
    comite_compliance:       float = 0.0

    # CapacitaciÃ³n
    pct_personal_capacitado: float = 0.0   # 0-100
    modulos_completados:     int   = 0
    modulos_totales:         int   = 6

    # Due Diligence
    proveedores_evaluados:   int   = 0
    proveedores_totales:     int   = 1     # evitar div/0

    # Riesgo
    mapa_riesgo_actualizado: bool  = False
    meses_desde_actualizacion: int = 99

    # ComunicaciÃ³n
    canal_operativo:         bool  = False
    denuncias_gestionadas:   bool  = False

    # InvestigaciÃ³n
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
    # PenalizaciÃ³n progresiva por antigÃ¼edad (mÃ¡x 12 meses)
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


# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# LEI ANTICORRUPÃÃO 12.846/2013 â BRASIL
# ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

ELEMENTOS_LEI_12846 = [
    # Obligatorios (peso 1.5)
    {"id": "programa_integridade",    "label": "Programa de Integridade formal",                       "tipo": "obrigatorio", "art": "Art. 41-D.1"},
    {"id": "codigo_conduta",          "label": "CÃ³digo de Conduta e Ãtica",                            "tipo": "obrigatorio", "art": "Art. 41-D.2"},
    {"id": "responsavel_compliance",  "label": "ResponsÃ¡vel pelo Compliance designado",                "tipo": "obrigatorio", "art": "Art. 41-D.3"},
    {"id": "treinamentos",            "label": "Treinamentos periÃ³dicos (dir. e funcionÃ¡rios)",        "tipo": "obrigatorio", "art": "Art. 41-D.4"},
    {"id": "canal_denuncia",          "label": "Canal de denÃºncia com proteÃ§Ã£o ao denunciante",        "tipo": "obrigatorio", "art": "Art. 41-D.5"},
    {"id": "due_diligence_terceiros", "label": "Due diligence de terceiros e fornecedores",            "tipo": "obrigatorio", "art": "Art. 41-D.6"},
    # Opcionales / Atenuantes (peso 1.0)
    {"id": "acordo_leniencia",        "label": "Acordo de LeniÃªncia â mecanismo documentado",         "tipo": "atenuante",   "art": "Art. 16"},
    {"id": "auditoria_interna",       "label": "Auditoria interna independente",                       "tipo": "atenuante",   "art": "Art. 41-D.8"},
    {"id": "controles_contabeis",     "label": "Controles contÃ¡beis e registros financeiros precisos", "tipo": "atenuante",   "art": "Art. 41-D.9"},
    {"id": "politica_doacoes",        "label": "PolÃ­tica de doaÃ§Ãµes e patrocÃ­nios",                   "tipo": "atenuante",   "art": "Art. 41-D.10"},
    {"id": "monitoramento",           "label": "Monitoramento contÃ­nuo e avaliaÃ§Ã£o periÃ³dica",         "tipo": "atenuante",   "art": "Art. 41-D.11"},
]

PESOS_LEI_12846 = {"obrigatorio": 1.5, "atenuante": 1.0}

NIVELES_LEI_12846 = [
    (0,   40,  "Incipiente",    "#dc2626"),
    (40,  65,  "Em AdequaÃ§Ã£o",  "#f59e0b"),
    (65,  80,  "Adequado",      "#3b82f6"),
    (80,  101, "Exemplar",      "#16a34a"),
]


@dataclass
class DadosLei12846:
    """Datos de entrada para el score de la Lei AnticorrupÃ§Ã£o 12.846."""
    # Obligatorios (0-100)
    programa_integridade:    float = 0.0
    codigo_conduta:          float = 0.0
    responsavel_compliance:  float = 0.0
    treinamentos:            float = 0.0
    canal_denuncia:          float = 0.0
    due_diligence_terceiros: float = 0.0
    # Atenuantes (0-100)
    acordo_leniencia:        float = 0.0
    auditoria_interna:       float = 0.0
    controles_contabeis:     float = 0.0
    politica_doacoes:        float = 0.0
    monitoramento:           float = 0.0

    extra: dict[str, Any] = field(default_factory=dict)


def calcular_score_lei_12846(d: DadosLei12846) -> dict:
    """
    Calcula el score para la Lei AnticorrupÃ§Ã£o 12.846/2013 (Brasil).
    Pesos diferenciados: obligatorios x1.5, atenuantes x1.0.
    Retorna score 0-100, nivel, color y detalle por elemento.
    """
    valores = {
        "programa_integridade":    d.programa_integridade,
        "codigo_conduta":          d.codigo_conduta,
        "responsavel_compliance":  d.responsavel_compliance,
        "treinamentos":            d.treinamentos,
        "canal_denuncia":          d.canal_denuncia,
        "due_diligence_terceiros": d.due_diligence_terceiros,
        "acordo_leniencia":        d.acordo_leniencia,
        "auditoria_interna":       d.auditoria_interna,
        "controles_contabeis":     d.controles_contabeis,
        "politica_doacoes":        d.politica_doacoes,
        "monitoramento":           d.monitoramento,
    }

    suma_ponderada = 0.0
    suma_pesos = 0.0
    detalle = []

    for elem in ELEMENTOS_LEI_12846:
        peso = PESOS_LEI_12846[elem["tipo"]]
        valor = valores.get(elem["id"], 0.0)
        suma_ponderada += valor * peso
        suma_pesos += 100 * peso
        detalle.append({
            "id":     elem["id"],
            "label":  elem["label"],
            "tipo":   elem["tipo"],
            "art":    elem["art"],
            "valor":  round(valor, 1),
            "estado": "completo" if valor >= 80 else "en_progreso" if valor >= 40 else "pendiente",
        })

    score = round((suma_ponderada / suma_pesos) * 100, 1) if suma_pesos > 0 else 0.0

    nivel, color = "Incipiente", "#dc2626"
    for minimo, maximo, nombre, clr in NIVELES_LEI_12846:
        if minimo <= score < maximo:
            nivel, color = nombre, clr
            break

    obrigatorios_ok  = sum(1 for e in detalle if e["tipo"] == "obrigatorio" and e["estado"] == "completo")
    obrigatorios_tot = sum(1 for e in detalle if e["tipo"] == "obrigatorio")

    return {
        "score":             score,
        "nivel":             nivel,
        "color":             color,
        "obrigatorios_ok":   obrigatorios_ok,
        "obrigatorios_total": obrigatorios_tot,
        "atenuantes_ok":     sum(1 for e in detalle if e["tipo"] == "atenuante" and e["estado"] == "completo"),
        "detalle":           detalle,
        "elegivel_reducao_multa": obrigatorios_ok >= 4,  # Art. 7 â criterio CGU
    }


def score_lei_12846_desde_dict(data: dict) -> dict:
    """Wrapper para llamar desde la API con un dict JSON."""
    campos = DadosLei12846.__dataclass_fields__
    d = DadosLei12846(**{k: v for k, v in data.items() if k in campos})
    return calcular_score_lei_12846(d)
