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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def _resumir(alerta: dict):
    """Llama al resumidor IA. Falla silenciosamente si no hay API key."""
    try:
        from scripts.ia_alertas import resumir_alerta
        return resumir_alerta(alerta)
    except Exception:
        return None
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
        "url": "https://www.argentina.gob.ar/anticorrupcion/noticias",
        "tipo": "html",
    },
    "uif": {
        "nombre": "Unidad de Información Financiera",
        "url": "https://www.argentina.gob.ar/uif/resoluciones-uif-generales",
        "tipo": "html",
    },
    "ocde": {
        "nombre": "OCDE — Anti-Bribery",
        "url": "https://www.oecd.org/daf/anti-bribery/",
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
    """Parser OA — extrae noticias de la Oficina Anticorrupción."""
    alertas = []
    KW = re.compile(
        r"integridad|compliance|resolución|programa|capacitación|"
        r"conflicto|denuncia|transparencia|ética|corrupción",
        re.I,
    )
    # La página de noticias tiene artículos con fecha y título
    for item in soup.select("article, .views-row, .noticias-item, h3, h2")[:12]:
        titulo = item.get_text(separator=" ", strip=True)[:140]
        if len(titulo) < 20 or not KW.search(titulo):
            continue
        # Intentar extraer fecha del texto
        m_fecha = re.search(r"(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", titulo)
        alertas.append({
            "id": f"oa_{hash(titulo) & 0xFFFF:04x}",
            "descripcion": titulo,
            "severidad": "verde",
            "categoria": "normativa_oa",
            "vencimiento": None,
            "fuente": "Oficina Anticorrupción",
            "fecha_deteccion": date.today().isoformat(),
            "metadata": {"fecha_noticia": m_fecha.group(1) if m_fecha else None},
        })
    return alertas[:4]


def _parsear_uif(soup: BeautifulSoup) -> list[dict]:
    """Parser UIF — extrae resoluciones generales con número y link."""
    alertas = []
    # La página tiene links con formato "NN/YYYY" apuntando a SAIJ
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        texto = a.get_text(strip=True)
        # Formato: "35/2026" con href a normativa/nacional
        if re.match(r"\d+/\d{4}$", texto) and "normativa" in href:
            num, anio = texto.split("/")
            desc = f"UIF Resolución {texto} — Norma AML/CFT vigente. Verificar aplicabilidad a su sector."
            alertas.append({
                "id": f"uif_{hash(texto) & 0xFFFF:04x}",
                "descripcion": desc,
                "severidad": "naranja" if int(anio) >= 2023 else "verde",
                "categoria": "normativa_aml",
                "vencimiento": None,
                "fuente": f"UIF — Res. {texto}",
                "fecha_deteccion": date.today().isoformat(),
                "metadata": {"numero": texto, "url_saij": href.replace("blank:#", "")},
            })
    return alertas[:5]


# Alertas OCDE curadas (la web bloquea scrapers con 403)
_OCDE_CURADAS = [
    {
        "id": "ocde_2026a",
        "descripcion": (
            "OCDE Anti-Corruption & Integrity Outlook 2026 — Publicado marzo 2026. "
            "Analiza tendencias globales en integridad pública, nuevas recomendaciones "
            "para el sector privado y avances en la Convención Anti-Soborno."
        ),
        "severidad": "verde",
        "categoria": "internacional_ocde",
        "vencimiento": None,
        "fuente": "OCDE — Anti-Bribery 2026",
        "metadata": {"url": "https://www.oecd.org/daf/anti-bribery/"},
    },
    {
        "id": "ocde_2026b",
        "descripcion": (
            "OCDE — Sanctioning foreign bribery through multijurisdictional resolutions "
            "(mayo 2026). Guía para empresas con operaciones en múltiples jurisdicciones "
            "sobre coordinación de sanciones y acuerdos de resolución."
        ),
        "severidad": "verde",
        "categoria": "internacional_ocde",
        "vencimiento": None,
        "fuente": "OCDE — Anti-Bribery 2026",
        "metadata": {"url": "https://www.oecd.org/daf/anti-bribery/"},
    },
    {
        "id": "ocde_2026c",
        "descripcion": (
            "OCDE Argentina — Indicadores de integridad pública 2026 presentados "
            "ante la Oficina Anticorrupción (mayo 2026). Evalúa transparencia, "
            "gestión de riesgos y cultura organizacional del sector público."
        ),
        "severidad": "verde",
        "categoria": "internacional_ocde",
        "vencimiento": None,
        "fuente": "OCDE — Argentina 2026",
        "metadata": {"url": "https://www.oecd.org/daf/anti-bribery/"},
    },
]


def _parsear_ocde(soup: BeautifulSoup) -> list[dict]:
    """Parser OCDE — intenta scraping, cae en curadas si hay 403."""
    alertas = []
    hoy = date.today().isoformat()
    for item in soup.select(".card, article, .list-item, .publication-item")[:8]:
        titulo = item.get_text(separator=" ", strip=True)[:150]
        if len(titulo) < 15:
            continue
        tipo = "Reporte" if "report" in titulo.lower() else "Publicación"
        alertas.append({
            "id": f"ocde_{hash(titulo) & 0xFFFF:04x}",
            "descripcion": f"OCDE Anti-Bribery — {tipo}: {titulo[:110]}",
            "severidad": "verde",
            "categoria": "internacional_ocde",
            "vencimiento": None,
            "fuente": "OCDE — Anti-Bribery",
            "fecha_deteccion": hoy,
        })
    # Si el scraping no dio resultados (403 u otro), usar curadas
    if not alertas:
        alertas = [{**a, "fecha_deteccion": hoy} for a in _OCDE_CURADAS]
    return alertas[:3]


PARSERS = {
    "oa":   _parsear_oa,
    "uif":  _parsear_uif,
    "ocde": _parsear_ocde,
}

# Alias de categorías para display
CATEGORIAS_LABEL = {
    "normativa_oa":     "Oficina Anticorrupción",
    "normativa_aml":    "UIF — AML/CFT",
    "internacional_ocde": "OCDE",
    "normativa_igj":    "IGJ — Normativa",
    "societario_igj":   "IGJ — Societario",
    "due_diligence_igj": "IGJ — Due Diligence",
    "programa":         "Programa de Integridad",
    "riesgo":           "Gestión de Riesgos",
    "capacitacion":     "Capacitación",
}


def correr_etl() -> list[dict]:
    """Scraping de todas las fuentes + alertas de vencimiento."""
    todas: list[dict] = list(ALERTAS_VENCIMIENTO)

    for clave, fuente in FUENTES.items():
        log.info(f"Scrapeando {fuente['nombre']} ...")
        soup = _fetch_html(fuente["url"])
        # Siempre llamar al parser: algunos (ej. OCDE) tienen fallback curado si soup es None
        nuevas = PARSERS[clave](soup) if soup else PARSERS[clave](BeautifulSoup("", "html.parser"))
        if nuevas:
            log.info(f"  → {len(nuevas)} alertas encontradas")
            todas.extend(nuevas)
        else:
            log.warning(f"  → Sin resultados para {clave}")

    # ── Enriquecer con resumen IA ──────────────────────────────────────────
    log.info("Generando resúmenes IA ...")
    for alerta in todas:
        if not alerta.get("resumen_ia"):
            resumen = _resumir(alerta)
            if resumen:
                alerta["resumen_ia"] = resumen
                log.info(f"  ✓ Resumen generado para {alerta['id']}")

    # Persistir resultado
    # ── IGJ mejorado ──────────────────────────────────────────────────────
    log.info("Corriendo módulo IGJ mejorado ...")
    try:
        import importlib.util, pathlib
        _igj_path = pathlib.Path(__file__).parent / "igj_alertas.py"
        _spec = importlib.util.spec_from_file_location("igj_alertas", _igj_path)
        _mod  = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        igj_alertas = _mod.correr_igj()
        log.info(f"  → {len(igj_alertas)} alertas IGJ")
        todas.extend(igj_alertas)
    except Exception as e:
        log.warning(f"  → IGJ error: {e}")

    resultado = {
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
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
        "actualizado": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "total": len(alertas),
        "alertas": alertas,
    }


if __name__ == "__main__":
    correr_etl()
