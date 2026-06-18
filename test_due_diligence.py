"""tests/test_due_diligence.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import re


def _limpiar_cuit(cuit: str) -> str:
    return re.sub(r"[^0-9]", "", cuit)


def test_limpiar_cuit_con_guiones():
    assert _limpiar_cuit("30-71234567-8") == "30712345678"


def test_limpiar_cuit_sin_guiones():
    assert _limpiar_cuit("30712345678") == "30712345678"


def test_cuit_invalido_vacio():
    assert _limpiar_cuit("") == ""


def test_verificar_cuit_estructura():
    """La respuesta debe tener los campos esperados."""
    from scripts.api_compliance import _verificar_cuit
    r = _verificar_cuit("30712345678")
    assert "cuit" in r
    assert "valido" in r
    assert "afip" in r
    assert "uif" in r
    assert "ocde" in r
    assert "riesgo" in r


def test_verificar_cuit_invalido():
    from scripts.api_compliance import _verificar_cuit
    r = _verificar_cuit("123")
    assert r["valido"] is False
