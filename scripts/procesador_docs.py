"""
procesador_docs.py
Procesa documentos subidos por el consultor:
  - PDFs: extrae texto, detecta fecha, tipo de documento
  - XLSXs/CSVs: extrae filas relevantes (nÃ³minas, proveedores, riesgos)

No modifica config.js automÃ¡ticamente â devuelve datos para revisiÃ³n manual.
Ph.D. Vicente H. Monteverde Â· Ecosistema Transparencia
"""
from __future__ import annotations

import io
import json
import logging
import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)

# ââ Directorio base de uploads ââââââââââââââââââââââââââââââââââââââââââââââ
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", "data/uploads"))
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ââ Tipos de documento reconocidos âââââââââââââââââââââââââââââââââââââââââ
TIPOS_DOC = {
    "codigo_etica": {
        "label": "CÃ³digo de Ã©tica / conducta",
        "keywords": ["cÃ³digo de Ã©tica", "cÃ³digo de conducta", "code of ethics",
                     "codigo etica", "conducta empresarial", "etica empresarial"],
        "elemento": "codigo_etica",
        "icono": "ð",
    },
    "politica_regalos": {
        "label": "PolÃ­tica de regalos e invitaciones",
        "keywords": ["regalos", "invitaciones", "gifts", "hospitality",
                     "obsequios", "polÃ­tica de regalos"],
        "elemento": "politica_regalos",
        "icono": "ð",
    },
    "politica_ddjj": {
        "label": "Declaraciones juradas de conflicto de interÃ©s",
        "keywords": ["declaraciÃ³n jurada", "conflicto de interÃ©s", "conflict of interest",
                     "ddjj", "declaracion jurada"],
        "elemento": "politica_ddjj",
        "icono": "ð",
    },
    "procedimiento_investigacion": {
        "label": "Procedimiento de investigaciones internas",
        "keywords": ["investigaciÃ³n interna", "investigaciones", "procedimiento disciplinario",
                     "internal investigation"],
        "elemento": "investigaciones",
        "icono": "ð",
    },
    "manual_compliance": {
        "label": "Manual de compliance / programa de integridad",
        "keywords": ["programa de integridad", "manual de compliance", "compliance program",
                     "integrity program", "programa anticorrupciÃ³n"],
        "elemento": "analisis_riesgos",
        "icono": "ð",
    },
    "constancia_rite": {
        "label": "Constancia de registro RITE",
        "keywords": ["rite", "registro de integridad", "oficina anticorrupciÃ³n",
                     "certificaciÃ³n rite", "nivel de madurez"],
        "elemento": "rite",
        "icono": "ðï¸",
    },
    "nomina_capacitados": {
        "label": "NÃ³mina de personal capacitado",
        "keywords": ["nÃ³mina", "capacitaciÃ³n", "training", "personal capacitado",
                     "empleados capacitados", "modulo"],
        "elemento": "capacitacion",
        "icono": "ð¥",
    },
    "listado_proveedores": {
        "label": "Listado de proveedores activos",
        "keywords": ["proveedores", "vendors", "suppliers", "terceros",
                     "proveedor", "cuit proveedor"],
        "elemento": "due_diligence",
        "icono": "ð¢",
    },
    "mapa_riesgos": {
        "label": "Mapa / matriz de riesgos",
        "keywords": ["mapa de riesgos", "matriz de riesgos", "risk map", "risk matrix",
                     "evaluaciÃ³n de riesgos", "probabilidad", "impacto"],
        "elemento": "analisis_riesgos",
        "icono": "ðºï¸",
    },
    "contratos_estado": {
        "label": "Contratos con sector pÃºblico",
        "keywords": ["licitaciÃ³n", "contrato estatal", "contrataciÃ³n pÃºblica",
                     "sector pÃºblico", "estado nacional", "municipio"],
        "elemento": "reglas_licitacion",
        "icono": "ð",
    },
}


# ââ DetecciÃ³n de fecha en texto âââââââââââââââââââââââââââââââââââââââââââââ
_PATRONES_FECHA = [
    r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})\b",        # dd/mm/yyyy
    r"\b(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})\b",        # yyyy-mm-dd
    r"\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b",          # 15 de marzo de 2024
]

_MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def _extraer_fecha(texto: str) -> Optional[str]:
    """Busca la primera fecha vÃ¡lida en el texto."""
    for patron in _PATRONES_FECHA:
        for m in re.finditer(patron, texto.lower()):
            try:
                grupos = m.groups()
                if len(grupos) == 3:
                    if grupos[1] in _MESES_ES:
                        d, mes_str, y = grupos
                        dt = date(int(y), _MESES_ES[mes_str], int(d))
                    elif len(grupos[0]) == 4:
                        y, mo, d = grupos
                        dt = date(int(y), int(mo), int(d))
                    else:
                        d, mo, y = grupos
                        dt = date(int(y), int(mo), int(d))
                    if 2015 <= dt.year <= 2030:
                        return dt.isoformat()
            except (ValueError, KeyError):
                continue
    return None


# ââ DetecciÃ³n de tipo de documento ââââââââââââââââââââââââââââââââââââââââââ
def _detectar_tipo(texto: str, nombre_archivo: str) -> str:
    """Detecta el tipo de documento por keywords en texto y nombre."""
    texto_lower = (texto + " " + nombre_archivo).lower()
    mejor = None
    mejor_hits = 0
    for tipo_id, meta in TIPOS_DOC.items():
        hits = sum(1 for kw in meta["keywords"] if kw in texto_lower)
        if hits > mejor_hits:
            mejor_hits = hits
            mejor = tipo_id
    return mejor or "otro"


# ââ Extractor PDF ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def _procesar_pdf(contenido: bytes, nombre: str) -> dict:
    """Extrae texto y metadata de un PDF."""
    resultado = {
        "tipo_detectado": "otro",
        "texto_preview": "",
        "fecha_detectada": None,
        "paginas": 0,
        "extraccion": "ok",
    }
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            resultado["paginas"] = len(pdf.pages)
            # Extraer texto de las primeras 3 pÃ¡ginas
            texto = ""
            for page in pdf.pages[:3]:
                t = page.extract_text() or ""
                texto += t + "\n"
            resultado["texto_preview"] = texto[:800].strip()
            resultado["fecha_detectada"] = _extraer_fecha(texto)
            resultado["tipo_detectado"] = _detectar_tipo(texto, nombre)
    except ImportError:
        # Fallback si no hay pdfplumber â solo detecta por nombre
        resultado["tipo_detectado"] = _detectar_tipo("", nombre)
        resultado["extraccion"] = "sin_pdfplumber"
    except Exception as e:
        resultado["extraccion"] = f"error: {str(e)[:80]}"
        resultado["tipo_detectado"] = _detectar_tipo("", nombre)
    return resultado


# ââ Extractor XLSX/CSV âââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def _procesar_xlsx(contenido: bytes, nombre: str) -> dict:
    """Extrae filas y columnas clave de un Excel o CSV."""
    resultado = {
        "tipo_detectado": "otro",
        "filas": 0,
        "columnas": [],
        "preview": [],
        "cuits_detectados": [],
        "extraccion": "ok",
    }
    try:
        import openpyxl  # type: ignore
        wb = openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)
        ws = wb.active
        filas = list(ws.iter_rows(values_only=True))
        if not filas:
            resultado["extraccion"] = "vacio"
            return resultado

        encabezados = [str(c).strip() if c is not None else "" for c in filas[0]]
        resultado["columnas"] = encabezados
        resultado["filas"] = len(filas) - 1

        # Preview primeras 5 filas
        preview = []
        for fila in filas[1:6]:
            row = {encabezados[i]: str(v) if v is not None else ""
                   for i, v in enumerate(fila) if i < len(encabezados)}
            preview.append(row)
        resultado["preview"] = preview

        # Detectar CUITs en cualquier columna
        cuits = set()
        patron_cuit = re.compile(r"\b\d{2}-?\d{8}-?\d\b")
        for fila in filas[1:]:
            for celda in fila:
                if celda and patron_cuit.search(str(celda)):
                    cuit = re.sub(r"[^0-9\-]", "", str(celda))
                    cuits.add(cuit)
        resultado["cuits_detectados"] = list(cuits)[:50]  # mÃ¡x 50

        # Detectar tipo por columnas y nombre
        texto_meta = " ".join(encabezados) + " " + nombre
        resultado["tipo_detectado"] = _detectar_tipo(texto_meta, nombre)

    except ImportError:
        resultado["extraccion"] = "sin_openpyxl"
        resultado["tipo_detectado"] = _detectar_tipo("", nombre)
    except Exception as e:
        resultado["extraccion"] = f"error: {str(e)[:80]}"
    return resultado


def _procesar_csv(contenido: bytes, nombre: str) -> dict:
    """Extrae datos de un CSV."""
    resultado = {
        "tipo_detectado": "otro",
        "filas": 0,
        "columnas": [],
        "preview": [],
        "cuits_detectados": [],
        "extraccion": "ok",
    }
    try:
        import csv
        texto = contenido.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(texto))
        filas = list(reader)
        resultado["filas"] = len(filas)
        resultado["columnas"] = list(reader.fieldnames or [])
        resultado["preview"] = filas[:5]

        patron_cuit = re.compile(r"\b\d{2}-?\d{8}-?\d\b")
        cuits = set()
        for fila in filas:
            for v in fila.values():
                if v and patron_cuit.search(str(v)):
                    cuits.add(re.sub(r"[^0-9\-]", "", str(v)))
        resultado["cuits_detectados"] = list(cuits)[:50]

        texto_meta = " ".join(resultado["columnas"]) + " " + nombre
        resultado["tipo_detectado"] = _detectar_tipo(texto_meta, nombre)
    except Exception as e:
        resultado["extraccion"] = f"error: {str(e)[:80]}"
    return resultado


# ââ FunciÃ³n principal ââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def procesar_documento(contenido: bytes, nombre_archivo: str, tipo_forzado: str = "") -> dict:
    """
    Procesa un documento y retorna metadata estructurada.
    tipo_forzado: si el usuario seleccionÃ³ el tipo manualmente en el panel.
    """
    ext = Path(nombre_archivo).suffix.lower()
    ahora = datetime.now().isoformat()

    if ext == ".pdf":
        datos = _procesar_pdf(contenido, nombre_archivo)
    elif ext in (".xlsx", ".xls"):
        datos = _procesar_xlsx(contenido, nombre_archivo)
    elif ext == ".csv":
        datos = _procesar_csv(contenido, nombre_archivo)
    elif ext in (".doc", ".docx"):
        # Sin dependencia extra â solo detecciÃ³n por nombre
        datos = {
            "tipo_detectado": _detectar_tipo("", nombre_archivo),
            "extraccion": "docx_sin_soporte",
            "texto_preview": "",
            "fecha_detectada": None,
        }
    else:
        datos = {
            "tipo_detectado": "otro",
            "extraccion": "formato_no_soportado",
        }

    tipo_final = tipo_forzado if tipo_forzado in TIPOS_DOC else datos.get("tipo_detectado", "otro")
    meta_tipo = TIPOS_DOC.get(tipo_final, {"label": "Otro documento", "icono": "ð", "elemento": ""})

    return {
        "nombre_archivo": nombre_archivo,
        "extension": ext,
        "tamanio_kb": round(len(contenido) / 1024, 1),
        "tipo": tipo_final,
        "tipo_label": meta_tipo["label"],
        "tipo_icono": meta_tipo["icono"],
        "elemento_compliance": meta_tipo.get("elemento", ""),
        "fecha_detectada": datos.get("fecha_detectada"),
        "extraccion": datos.get("extraccion", "ok"),
        "subido_en": ahora,
        "datos": {k: v for k, v in datos.items()
                  if k not in ("tipo_detectado", "extraccion", "fecha_detectada")},
    }


def guardar_documento(contenido: bytes, nombre_archivo: str, tipo: str) -> Path:
    """Guarda el archivo en data/uploads/{tipo}/"""
    carpeta = UPLOADS_DIR / tipo
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / nombre_archivo
    destino.write_bytes(contenido)
    return destino


def listar_documentos() -> list[dict]:
    """Lista todos los documentos subidos con su metadata."""
    docs = []
    registro = UPLOADS_DIR / "registro.json"
    if registro.exists():
        try:
            docs = json.loads(registro.read_text(encoding="utf-8"))
        except Exception:
            docs = []
    return docs


def registrar_documento(metadata: dict):
    """Agrega un documento al registro JSON central."""
    docs = listar_documentos()
    # Reemplaza si ya existe el mismo nombre+tipo
    docs = [d for d in docs
            if not (d["nombre_archivo"] == metadata["nombre_archivo"]
                    and d["tipo"] == metadata["tipo"])]
    docs.append(metadata)
    registro = UPLOADS_DIR / "registro.json"
    registro.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")


def eliminar_documento(nombre_archivo: str, tipo: str) -> bool:
    """Elimina un archivo del disco y del registro."""
    ruta = UPLOADS_DIR / tipo / nombre_archivo
    if ruta.exists():
        ruta.unlink()
    docs = listar_documentos()
    docs = [d for d in docs
            if not (d["nombre_archivo"] == nombre_archivo and d["tipo"] == tipo)]
    registro = UPLOADS_DIR / "registro.json"
    registro.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    return True
