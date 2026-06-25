"""
igj_alertas.py  —  Módulo IGJ mejorado
Fuentes:
  1. API datos.jus.gob.ar  → balances vencidos + entidades con baja
  2. argentina.gob.ar/igj  → resoluciones generales recientes
  3. Alertas curadas        → vencimientos regulatorios IGJ conocidos
"""
from __future__ import annotations

import csv
import io
import logging
import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ComplianceBot/1.0; "
        "+https://mapatransparencia-production.up.railway.app)"
    )
}
TIMEOUT = 18

# ── URLs ─────────────────────────────────────────────────────────────────────
URL_BALANCES = (
    "https://datos.jus.gob.ar/dataset/da045e06-35cb-4bdd-9b5e-ddee6712c86c"
    "/resource/7849ffd0-4a00-4223-acf7-0cce652fb949/download/igj-balances-muestreo.csv"
)
URL_ENTIDADES = (
    "https://datos.jus.gob.ar/dataset/da045e06-35cb-4bdd-9b5e-ddee6712c86c"
    "/resource/6652404c-7de4-45b5-8344-80f4bcc200f7/download/igj-entidades-muestreo.csv"
)
URL_IGJ_WEB = "https://www.argentina.gob.ar/justicia/igj"
BASE_GOB    = "https://www.argentina.gob.ar"

# Tipos societarios con obligación de presentar balance ante IGJ
TIPOS_OBLIG = {"50": "SA", "55": "SAU", "60": "SRL", "200": "SAS", "300": "Sucursal extranjera"}
MESES_ROJO    = 18
MESES_NARANJA = 12

# ── Alertas curadas (regulatorias IGJ conocidas) ─────────────────────────────
ALERTAS_IGJ_CURADAS: list[dict] = [
    {
        "id": "igj_c001",
        "descripcion": (
            "RG IGJ 5/2026 — Resoluciones particulares en formato digital desde 16/06/2026. "
            "Verificar habilitación TAD y CUIT asociado para recibir notificaciones."
        ),
        "severidad": "naranja",
        "categoria": "normativa_igj",
        "vencimiento": "2026-07-31",
        "fuente": "IGJ — RG 5/2026",
    },
    {
        "id": "igj_c002",
        "descripcion": (
            "IGJ implementa plancha de inscripción digital: elimina obligación de copias en papel. "
            "Actualizar procedimiento interno de inscripción de actas y poderes."
        ),
        "severidad": "verde",
        "categoria": "normativa_igj",
        "vencimiento": None,
        "fuente": "IGJ — Circular 2026",
    },
]


def _fetch_csv(url: str) -> list[dict]:
    """Descarga CSV y devuelve lista de dicts con keys limpias."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        text = r.content.decode("utf-8-sig")  # elimina BOM automáticamente
        reader = csv.DictReader(io.StringIO(text))
        return [{k.strip().strip('"'): (v or "").strip() for k, v in row.items()} for row in reader]
    except Exception as e:
        log.warning(f"IGJ CSV error ({url[-40:]}): {e}")
        return []


def alertas_balances_vencidos() -> list[dict]:
    """Detecta empresas con balances atrasados en el dataset público de IGJ."""
    alertas = []
    hoy = date.today()

    for row in _fetch_csv(URL_BALANCES):
        tipo = row.get("tipo_societario", "")
        if tipo not in TIPOS_OBLIG:
            continue
        razon     = row.get("razon_social", "").strip()
        fecha_str = row.get("fecha_balance", "").strip()
        if not razon or len(fecha_str) != 8:
            continue
        try:
            fb = date(int(fecha_str[:4]), int(fecha_str[4:6]), int(fecha_str[6:8]))
        except ValueError:
            continue

        meses = (hoy - fb).days // 30
        if meses < MESES_NARANJA:
            continue

        sev  = "rojo" if meses >= MESES_ROJO else "naranja"
        desc = (
            f"{razon} ({TIPOS_OBLIG[tipo]}) — balance al {fb.strftime('%d/%m/%Y')} "
            f"sin actualizar hace {meses} meses. "
            + ("Riesgo: multa IGJ + observación organismos de control." if sev == "rojo"
               else "Verificar estado de presentación ante IGJ.")
        )
        alertas.append({
            "id": f"igj_bal_{hash(razon + fecha_str) & 0xFFFF:04x}",
            "descripcion": desc,
            "severidad": sev,
            "categoria": "societario_igj",
            "vencimiento": None,
            "fuente": "IGJ — datos.jus.gob.ar",
            "fecha_deteccion": hoy.isoformat(),
            "metadata": {
                "razon_social": razon,
                "tipo": TIPOS_OBLIG[tipo],
                "fecha_balance": fb.isoformat(),
                "meses_atraso": meses,
            },
        })

    alertas.sort(key=lambda x: x["metadata"]["meses_atraso"], reverse=True)
    return alertas[:5]


def alertas_entidades_baja() -> list[dict]:
    """Detecta entidades dadas de baja (útil en due diligence de terceros)."""
    alertas = []
    hoy = date.today()

    for row in _fetch_csv(URL_ENTIDADES):
        tipo = row.get("tipo_societario", "")
        if tipo not in TIPOS_OBLIG:
            continue
        if not row.get("dada_de_baja", "").strip():
            continue
        razon   = row.get("razon_social", "").strip()
        detalle = row.get("detalle_baja", "").strip() or "sin detalle registrado"
        alertas.append({
            "id": f"igj_baja_{hash(razon) & 0xFFFF:04x}",
            "descripcion": (
                f"{razon} ({TIPOS_OBLIG[tipo]}) — entidad dada de baja en IGJ. "
                f"Motivo: {detalle}. Revisar en due diligence de terceros."
            ),
            "severidad": "naranja",
            "categoria": "due_diligence_igj",
            "vencimiento": None,
            "fuente": "IGJ — datos.jus.gob.ar",
            "fecha_deteccion": hoy.isoformat(),
        })
    return alertas[:3]


def alertas_resoluciones_web() -> list[dict]:
    """
    Extrae resoluciones generales IGJ desde argentina.gob.ar/justicia/igj.
    Devuelve las que tienen PDF de resolución.
    """
    alertas = []
    try:
        r = requests.get(URL_IGJ_WEB, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            texto = a.get_text(strip=True)
            # Solo PDFs de resoluciones generales
            if not re.search(r"rg_igj|resolucion.*igj|igj.*resol", href, re.I):
                continue

            url_full = href if href.startswith("http") else BASE_GOB + href
            # Extraer número desde la URL o el texto
            m = re.search(r"rg[_\-]igj[_\-](\d+)[_\-](\d{4})", href, re.I)
            ref = f"RG IGJ {m.group(1)}/{m.group(2)}" if m else "Resolución General IGJ"

            alertas.append({
                "id": f"igj_res_{hash(href) & 0xFFFF:04x}",
                "descripcion": (
                    f"{ref} — Nueva resolución general publicada. "
                    f"{texto[:80] if texto else 'Ver texto en IGJ.'}"
                ),
                "severidad": "naranja",
                "categoria": "normativa_igj",
                "vencimiento": None,
                "fuente": "IGJ — argentina.gob.ar",
                "fecha_deteccion": date.today().isoformat(),
                "metadata": {"url_pdf": url_full, "numero": ref},
            })

    except Exception as e:
        log.warning(f"IGJ web scraping error: {e}")

    return alertas[:3]


def correr_igj() -> list[dict]:
    """Punto de entrada: consolida todas las fuentes IGJ."""
    hoy = date.today().isoformat()

    log.info("IGJ ▸ balances vencidos (datos.jus.gob.ar)...")
    bal = alertas_balances_vencidos()
    log.info(f"  → {len(bal)} alertas")

    log.info("IGJ ▸ entidades con baja (datos.jus.gob.ar)...")
    bajas = alertas_entidades_baja()
    log.info(f"  → {len(bajas)} entidades")

    log.info("IGJ ▸ resoluciones web (argentina.gob.ar)...")
    res = alertas_resoluciones_web()
    log.info(f"  → {len(res)} resoluciones")

    # Agregar fecha_deteccion a las curadas
    curadas = [{**a, "fecha_deteccion": hoy} for a in ALERTAS_IGJ_CURADAS]

    total = curadas + res + bal + bajas
    log.info(f"IGJ total: {len(total)} alertas generadas")
    return total


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    for a in correr_igj():
        icon = {"rojo": "🔴", "naranja": "🟠", "verde": "🟢"}.get(a["severidad"], "⚪")
        print(f"{icon} [{a['categoria']:25}] {a['descripcion'][:95]}")