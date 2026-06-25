"""
AGREGAR ESTO A api_compliance.py
─────────────────────────────────
1. Al inicio, agregar a los imports existentes:
   from fastapi import File, UploadFile, Form
   from scripts.procesador_docs import (
       procesar_documento, guardar_documento,
       registrar_documento, listar_documentos, eliminar_documento,
       TIPOS_DOC
   )

2. Pegar los endpoints de abajo junto a los demás @router endpoints.
"""

# ── Endpoints de carga de documentos ────────────────────────────────────────

@router.get("/documentos-cliente")
async def get_documentos_cliente():
    """Lista todos los documentos subidos con su metadata."""
    docs = listar_documentos()
    # Calcular completitud por elemento de compliance
    elementos_cubiertos = {d["elemento_compliance"] for d in docs if d.get("elemento_compliance")}
    total_tipos = len(TIPOS_DOC)
    return {
        "total": len(docs),
        "completitud_pct": round(len(elementos_cubiertos) / total_tipos * 100),
        "elementos_cubiertos": list(elementos_cubiertos),
        "documentos": docs,
    }


@router.get("/documentos-cliente/tipos")
async def get_tipos_documentos():
    """Devuelve los tipos de documento reconocidos por el sistema."""
    return {
        "tipos": [
            {"id": k, "label": v["label"], "icono": v["icono"], "elemento": v["elemento"]}
            for k, v in TIPOS_DOC.items()
        ]
    }


@router.post("/documentos-cliente/upload")
async def upload_documento(
    archivo: UploadFile = File(...),
    tipo_forzado: str = Form(""),  # el consultor puede forzar el tipo desde el panel
):
    """
    Sube un documento y lo procesa.
    Formatos soportados: PDF, XLSX, XLS, CSV, DOC, DOCX.
    """
    EXTENSIONES_OK = {".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx"}
    MAX_MB = 20

    ext = Path(archivo.filename).suffix.lower()
    if ext not in EXTENSIONES_OK:
        raise HTTPException(
            status_code=415,
            detail=f"Formato no soportado: {ext}. Usar: {', '.join(EXTENSIONES_OK)}"
        )

    contenido = await archivo.read()
    if len(contenido) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Archivo mayor a {MAX_MB} MB")

    # Procesar
    metadata = procesar_documento(contenido, archivo.filename, tipo_forzado)

    # Guardar en disco
    guardar_documento(contenido, archivo.filename, metadata["tipo"])

    # Registrar en JSON
    registrar_documento(metadata)

    return {
        "ok": True,
        "mensaje": f"'{archivo.filename}' subido correctamente",
        "metadata": metadata,
    }


@router.delete("/documentos-cliente/{tipo}/{nombre_archivo}")
async def delete_documento(tipo: str, nombre_archivo: str):
    """Elimina un documento del registro y del disco."""
    eliminar_documento(nombre_archivo, tipo)
    return {"ok": True, "mensaje": f"'{nombre_archivo}' eliminado"}


@router.get("/documentos-cliente/checklist")
async def checklist_documentacion():
    """
    Devuelve qué documentos están cubiertos y cuáles faltan,
    mapeados a los elementos del programa de integridad.
    """
    docs = listar_documentos()
    elementos_subidos = {}
    for d in docs:
        elem = d.get("elemento_compliance", "")
        if elem and elem not in elementos_subidos:
            elementos_subidos[elem] = {
                "archivo": d["nombre_archivo"],
                "fecha": d.get("fecha_detectada"),
                "subido_en": d.get("subido_en"),
            }

    checklist = []
    for tipo_id, meta in TIPOS_DOC.items():
        elem = meta.get("elemento", "")
        cubierto = elem in elementos_subidos
        checklist.append({
            "tipo": tipo_id,
            "label": meta["label"],
            "icono": meta["icono"],
            "elemento_compliance": elem,
            "cubierto": cubierto,
            "archivo": elementos_subidos.get(elem, {}).get("archivo"),
            "fecha": elementos_subidos.get(elem, {}).get("fecha"),
        })

    cubiertos = sum(1 for c in checklist if c["cubierto"])
    return {
        "cubiertos": cubiertos,
        "total": len(checklist),
        "pct": round(cubiertos / len(checklist) * 100),
        "checklist": checklist,
    }
