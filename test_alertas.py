"""tests/test_alertas.py"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from scripts.etl_alertas import ALERTAS_VENCIMIENTO


def test_alertas_vencimiento_tienen_campos():
    """Todas las alertas base deben tener los campos obligatorios."""
    campos = {"id", "descripcion", "severidad", "categoria"}
    for alerta in ALERTAS_VENCIMIENTO:
        assert campos.issubset(alerta.keys()), f"Faltan campos en: {alerta}"


def test_severidades_validas():
    """Las severidades deben ser rojo, naranja o verde."""
    validas = {"rojo", "naranja", "verde"}
    for alerta in ALERTAS_VENCIMIENTO:
        assert alerta["severidad"] in validas, f"Severidad inválida: {alerta['severidad']}"


def test_cargar_alertas_retorna_dict(tmp_path, monkeypatch):
    """cargar_alertas() retorna dict con clave 'alertas'."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    # Crear archivo de caché artificial
    cache = {
        "actualizado": "2026-01-01T00:00:00Z",
        "total": 2,
        "alertas": ALERTAS_VENCIMIENTO[:2],
    }
    (tmp_path / "alertas.json").write_text(json.dumps(cache))

    # Re-importar con el monkeypatch activo
    import importlib
    import scripts.etl_alertas as mod
    importlib.reload(mod)

    data = mod.cargar_alertas()
    assert "alertas" in data
    assert isinstance(data["alertas"], list)
