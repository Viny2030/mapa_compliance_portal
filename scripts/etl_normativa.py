"""
etl_normativa.py
Actualiza el catálogo de normativa compliance desde fuentes oficiales:
InfoLEG, Boletín Oficial, OCDE, GAFI/FATF.
"""
from __future__ import annotations
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
NORMATIVA_FILE = DATA_DIR / "normativa.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ComplianceBot/1.0"}
TIMEOUT = 20

# Categorías del dashboard (8 categorías de la pestaña Legislación)
CATEGORIAS = {
    "antisoborno":      "Antisoborno & Integridad",
    "aml":              "Lavado de Activos (AML/CFT)",
    "datos_personales": "Protección de Datos Personales",
    "mercado_cap":      "Mercado de Capitales",
    "laboral":          "Laboral & DDHH",
    "ambiental":        "Ambiental (ESG)",
    "competencia":      "Defensa de la Competencia",
    "internacional":    "Normativa Internacional",
}

# Normativa base — siempre presente (no depende de scraping)
NORMATIVA_BASE: list[dict] = [
    # Antisoborno
    {"id": "l27401", "nombre": "Ley 27.401", "descripcion": "Responsabilidad Penal Empresaria",
     "categoria": "antisoborno", "pais": "AR", "organismo": "Congreso Nacional",
     "vigente": True, "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/305000-309999/305274/norma.htm"},
    {"id": "res24_oa", "nombre": "Resolución 24/2018 OA", "descripcion": "Pautas mínimas programa de integridad",
     "categoria": "antisoborno", "pais": "AR", "organismo": "OA",
     "vigente": True, "url": "https://www.argentina.gob.ar/normativa/nacional/resolución-24-2018-306905"},
    {"id": "fcpa", "nombre": "FCPA", "descripcion": "Foreign Corrupt Practices Act",
     "categoria": "antisoborno", "pais": "US", "organismo": "DOJ / SEC",
     "vigente": True, "url": "https://www.justice.gov/criminal/criminal-fraud/fcpa"},
    {"id": "ukba", "nombre": "UK Bribery Act 2010", "descripcion": "Ley antisoborno Reino Unido",
     "categoria": "antisoborno", "pais": "GB", "organismo": "UK Parliament",
     "vigente": True, "url": "https://www.legislation.gov.uk/ukpga/2010/23/contents"},
    {"id": "sapin2", "nombre": "Loi Sapin II", "descripcion": "Transparencia, lucha contra la corrupción y modernización de la vida económica (Ley n.º 2016-1691). Obliga a empresas de +500 empleados y crea la AFA y el CJIP.",
     "categoria": "antisoborno", "pais": "FR", "organismo": "AFA (Agence Française Anticorruption)",
     "vigente": True, "url": "https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000033558528"},
    {"id": "lei12846", "nombre": "Lei 12.846/2013", "descripcion": "Lei Anticorrupção — responsabilidad administrativa y civil objetiva de personas jurídicas por actos contra la administración pública (Brasil).",
     "categoria": "antisoborno", "pais": "BR", "organismo": "Presidência da República / CGU",
     "vigente": True, "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12846.htm"},
    {"id": "l2_2023", "nombre": "Ley 2/2023", "descripcion": "Reguladora de la protección de las personas que informen sobre infracciones normativas y de lucha contra la corrupción (España). Transpone la Directiva UE 2019/1937.",
     "categoria": "antisoborno", "pais": "ES", "organismo": "Cortes Generales / BOE",
     "vigente": True, "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2023-4513"},
    {"id": "eu_dir_2019_1937", "nombre": "Directiva (UE) 2019/1937", "descripcion": "Protección de las personas que informan sobre infracciones del Derecho de la Unión (whistleblowing). Obliga a canales de denuncia en empresas de +50 empleados.",
     "categoria": "antisoborno", "pais": "EU", "organismo": "Parlamento Europeo / Consejo UE",
     "vigente": True, "url": "https://eur-lex.europa.eu/eli/dir/2019/1937/oj/eng"},
    {"id": "iso37001", "nombre": "ISO 37001", "descripcion": "Sistema de Gestión Antisoborno — requisitos con orientación para su uso (ISO 37001:2016, revisada en 2025).",
     "categoria": "antisoborno", "pais": "INTL", "organismo": "ISO",
     "vigente": True, "url": "https://www.iso.org/standard/37001"},

    # AML
    {"id": "l25246", "nombre": "Ley 25.246", "descripcion": "Encubrimiento y Lavado de Activos",
     "categoria": "aml", "pais": "AR", "organismo": "Congreso / UIF",
     "vigente": True, "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/62977/texact.htm"},
    {"id": "gafi40", "nombre": "GAFI 40 Recomendaciones", "descripcion": "Estándar internacional AML/CFT",
     "categoria": "aml", "pais": "INTL", "organismo": "FATF/GAFI",
     "vigente": True, "url": "https://www.fatf-gafi.org/content/dam/fatf-gafi/recommendations/FATF%20Recommendations%202012.pdf"},

    # Datos personales
    {"id": "l25326", "nombre": "Ley 25.326", "descripcion": "Protección de Datos Personales (Argentina)",
     "categoria": "datos_personales", "pais": "AR", "organismo": "AAIP",
     "vigente": True, "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm"},
    {"id": "gdpr", "nombre": "GDPR", "descripcion": "Reglamento General de Protección de Datos (UE)",
     "categoria": "datos_personales", "pais": "EU", "organismo": "Parlamento Europeo",
     "vigente": True, "url": "https://gdpr-info.eu/"},

    # Internacional
    {"id": "ocde_conv", "nombre": "Convención OCDE Antisoborno", "descripcion": "Convención sobre el cohecho de servidores públicos extranjeros",
     "categoria": "internacional", "pais": "INTL", "organismo": "OCDE",
     "vigente": True, "url": "https://www.oecd.org/corruption/oecdantibriberyconvention.htm"},
    {"id": "uncac", "nombre": "UNCAC", "descripcion": "Convención ONU contra la Corrupción",
     "categoria": "internacional", "pais": "INTL", "organismo": "ONU / UNODC",
     "vigente": True, "url": "https://www.unodc.org/unodc/en/corruption/uncac.html"},

    # Mercado de capitales
    {"id": "l26831", "nombre": "Ley 26.831", "descripcion": "Mercado de Capitales",
     "categoria": "mercado_cap", "pais": "AR", "organismo": "CNV",
     "vigente": True, "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/205000-209999/207860/norma.htm"},

    # Competencia
    {"id": "l27442", "nombre": "Ley 27.442", "descripcion": "Defensa de la Competencia",
     "categoria": "competencia", "pais": "AR", "organismo": "CNDC",
     "vigente": True, "url": "https://servicios.infoleg.gob.ar/infolegInternet/anexos/310000-314999/310855/norma.htm"},
]


def _buscar_actualizaciones_boletin() -> list[dict]:
    """Scraping ligero del Boletín Oficial para normas recientes de compliance."""
    url = "https://www.boletinoficial.gob.ar/"
    nuevas = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select(".normal-content li, .resultado a")[:20]:
            texto = item.get_text(strip=True)
            if re.search(r"integridad|compliance|UIF|anticorrupci", texto, re.I):
                nuevas.append({
                    "id": f"bo_{hash(texto) & 0xFFFF:04x}",
                    "nombre": texto[:80],
                    "descripcion": "Norma detectada en Boletín Oficial",
                    "categoria": "antisoborno",
                    "pais": "AR",
                    "organismo": "Boletín Oficial",
                    "vigente": True,
                    "url": url,
                    "fecha_deteccion": datetime.utcnow().date().isoformat(),
                })
    except Exception as e:
        log.warning(f"Error scraping Boletín Oficial: {e}")
    return nuevas[:5]


def correr_etl() -> list[dict]:
    todas = list(NORMATIVA_BASE)
    log.info("Buscando actualizaciones en Boletín Oficial ...")
    nuevas = _buscar_actualizaciones_boletin()
    log.info(f"  → {len(nuevas)} normas nuevas detectadas")
    todas.extend(nuevas)

    resultado = {
        "actualizado": datetime.utcnow().isoformat() + "Z",
        "total": len(todas),
        "categorias": CATEGORIAS,
        "normativa": todas,
    }
    NORMATIVA_FILE.write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    log.info(f"✓ {len(todas)} normas guardadas en {NORMATIVA_FILE}")
    return todas


def cargar_normativa() -> dict:
    if NORMATIVA_FILE.exists():
        return json.loads(NORMATIVA_FILE.read_text())
    correr_etl()
    return json.loads(NORMATIVA_FILE.read_text())


if __name__ == "__main__":
    correr_etl()
