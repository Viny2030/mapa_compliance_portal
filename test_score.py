"""tests/test_score.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.motor_score import calcular_score, DatosPrograma


def test_score_vacio():
    """Programa sin ningún elemento → score 0."""
    d = DatosPrograma()
    r = calcular_score(d)
    assert r["score_global"] == 0.0
    assert r["nivel"] == "Inicial"


def test_score_completo():
    """Programa 100% en todos los ejes → score ~100."""
    d = DatosPrograma(
        codigo_conducta=100, politicas_aprobadas=100, canal_denuncia=100,
        responsable_designado=100, comite_compliance=100,
        pct_personal_capacitado=100, modulos_completados=6, modulos_totales=6,
        proveedores_evaluados=100, proveedores_totales=100,
        mapa_riesgo_actualizado=True, meses_desde_actualizacion=0,
        canal_operativo=True, denuncias_gestionadas=True,
        procedimiento_escrito=True, investigaciones_abiertas=0,
    )
    r = calcular_score(d)
    assert r["score_global"] >= 95
    assert r["nivel"] == "Avanzado"


def test_score_parcial():
    """Score parcial debe quedar en rango correcto."""
    d = DatosPrograma(
        codigo_conducta=70, politicas_aprobadas=60, canal_denuncia=100,
        responsable_designado=100, comite_compliance=50,
        pct_personal_capacitado=65, modulos_completados=4, modulos_totales=6,
        proveedores_evaluados=10, proveedores_totales=20,
        mapa_riesgo_actualizado=True, meses_desde_actualizacion=3,
        canal_operativo=True, denuncias_gestionadas=False,
        procedimiento_escrito=True, investigaciones_abiertas=1,
    )
    r = calcular_score(d)
    assert 40 <= r["score_global"] <= 85
    assert "nivel" in r
    assert "ejes" in r
    assert len(r["ejes"]) == 6


def test_score_desde_dict():
    from scripts.motor_score import score_desde_dict
    data = {"codigo_conducta": 80, "canal_denuncia": 100, "responsable_designado": 100}
    r = score_desde_dict(data)
    assert "score_global" in r


def test_pesos_suman_100():
    from scripts.motor_score import PESOS
    assert sum(PESOS.values()) == 100
