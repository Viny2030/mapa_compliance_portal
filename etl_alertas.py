"""
etl_alertas.py
Scraper de alertas regulatorias: OA (Oficina Anticorrupción), UIF, OCDE.
Genera alertas clasificadas por severidad y las persiste en JSON.
"""
from __future__ import annotations
import json
import logging
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
ALERTAS_FILE = DATA_DIR / "alertas.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ComplianceBot/1.0; "
        "+https://mapatransparencia-production.up.railway.app)"
    )
}
TIMEOUT = 20

# ── Fuentes ────────────────────────────────────────────────────────────────
FUENTES = {
    "oa": {
        "nombre": "Oficina Anticorrupción",
        "url": "https://www.argentina.gob.ar/oficina-anticorrupcion/integridad-y-transparencia",
        "tipo": "html",
    },
    "uif": {
        "nombre": "Unidad de Información Financiera",
        "url": "https://www.argentina.gob.ar/uif/resoluciones",
        "tipo": "html",
    },
    "ocde": {
        "nombre": "OCDE — Anti-Bribery",
        "url": "https://www.oecd.org/en/topics/anti-bribery-and-corruption.html",
        "tipo": "html",
    },
}


# ── Alertas estáticas de vencimiento (se actualizan desde config) ──────────
ALERTAS_VENCIMIENTO: list[dict] = [
    {
        "id": "v001",
        "descripcion": "Renovación Canal de Denuncias — certificación anual",
        "severidad": "rojo",
        "categoria": "programa",
        "vencimiento": (date.today() + timedelta(days=15)).isoformat(),
        "fuente": "Interna",
    },
    {
        "id": "v002",
        "descripcion": "Actualización Mapa de Riesgos — revisión semestral",
        "severidad": "naranja",
        "categoria": "riesgo",
        "vencimiento": (date.today() + timedelta(days=45)).isoformat(),
        "fuente": "Ley 27.401 art. 23",
    },
    {
        "id": "v003",
        "descripcion": "Módulo de capacitación AML — cierre cohorte Q2",
        "severidad": "naranja",
        "categoria": "capacitacion",
        "vencimiento": (date.today() + timedelta(days=30)).isoformat(),
        "fuente": "UIF Res. 70/2011",
    },
]


def _fetch_html(url: str) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        log.warning(f"Error fetching {url}: {e}")
        return None


def _parsear_oa(soup: BeautifulSoup) -> list[dict]:
    alertas = []
    for item in soup.select("article, .card, .item-list li")[:10]:
        titulo = item.get_text(strip=True)[:120]
        if any(kw in titulo.lower() for kw in ["compliance", "integridad", "resolución", "programa"]):
            alertas.append({
                "id": f"oa_{hash(titulo) & 0xFFFF:04x}",
                "descripcion": titulo,
                "severidad": "naranja",
                "categoria": "normativa",
                "vencimiento": None,
                "fuente": "OA",
                "fecha_deteccion": date.today().isoformat(),
            })
    return alertas[:5]


def _parsear_uif(soup: BeautifulSoup) -> list[dict]:
    alertas = []
    for item in soup.select("article, .result-item, li.search-result")[:10]:
        titulo = item.get_text(strip=True)[:120]
        if re.search(r"resolución|circular|providencia", titulo, re.I):
            alertas.append({
                "id": f"uif_{hash(titulo) & 0xFFFF:04x}",
                "descripcion": titulo,
                "severidad": "naranja",
                "categoria": "normativa_aml",
                "vencimiento": None,
                "fuente": "UIF",
                "fecha_deteccion": date.today().isoformat(),
            })
    return alertas[:5]


def _parsear_ocde(soup: BeautifulSoup) -> list[dict]:
    alertas = []
    for item in soup.select("article, .featured-item, .list-item")[:5]:
        titulo = item.get_text(strip=True)[:120]
        alertas.append({
            "id": f"ocde_{hash(titulo) & 0xFFFF:04x}",
            "descripcion": titulo,
            "severidad": "verde",
            "categoria": "internacional",
            "vencimiento": None,
            "fuente": "OCDE",
            "fecha_deteccion": date.today().isoformat(),
        })
    return alertas[:3]


PARSERS = {
    "oa":   _parsear_oa,
    "uif":  _parsear_uif,
    "ocde": _parsear_ocde,
}


def correr_etl() -> list[dict]:
    """Scraping de todas las fuentes + alertas de vencimiento."""
    todas: list[dict] = list(ALERTAS_VENCIMIENTO)

    for clave, fuente in FUENTES.items():
        log.info(f"Scrapeando {fuente['nombre']} ...")
        soup = _fetch_html(fuente["url"])
        if soup:
            nuevas = PARSERS[clave](soup)
            log.info(f"  → {len(nuevas)} alertas encontradas")
            todas.extend(nuevas)
        else:
            log.warning(f"  → Sin resultados para {clave}")

    # Persistir resultado
    resultado = {
        "actualizado": datetime.utcnow().isoformat() + "Z",
        "total": len(todas),
        "alertas": todas,
    }
    ALERTAS_FILE.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    log.info(f"✓ {len(todas)} alertas guardadas en {ALERTAS_FILE}")
    return todas


def cargar_alertas() -> dict:
    """Carga las alertas desde el archivo JSON (caché)."""
    if ALERTAS_FILE.exists():
        return json.loads(ALERTAS_FILE.read_text())
    # Si no hay caché, correr ETL en el momento
    alertas = correr_etl()
    return {
        "actualizado": datetime.utcnow().isoformat() + "Z",
        "total": len(alertas),
        "alertas": alertas,
    }


if __name__ == "__main__":
    correr_etl()
