# INSTRUCCIONES DE INTEGRACIÓN — Módulo de carga de documentos
# =============================================================
# Ph.D. Vicente H. Monteverde · Ecosistema Transparencia

## PASO 1 — Copiar los archivos nuevos al proyecto

Desde el repo descargado, copiar:

  procesador_docs.py   →  scripts/procesador_docs.py
  upload_clientes.html →  upload_clientes.html

## PASO 2 — Modificar scripts/api_compliance.py

### 2a. Agregar imports (después de los imports existentes, línea ~15):

from fastapi import File, UploadFile, Form
from pathlib import Path
from scripts.procesador_docs import (
    procesar_documento, guardar_documento,
    registrar_documento, listar_documentos, eliminar_documento,
    TIPOS_DOC,
)

### 2b. Pegar los endpoints nuevos (al final del archivo, antes de la última línea):

Copiar todo el contenido de upload_endpoints.py y pegarlo al final de api_compliance.py.

## PASO 3 — Modificar main.py

### Agregar la ruta del nuevo HTML (después del endpoint /capacitaciones.html):

@app.get("/upload_clientes.html", include_in_schema=False)
async def upload_clientes_html():
    return FileResponse(os.path.join(ROOT, "upload_clientes.html"))

## PASO 4 — Agregar dependencias a requirements.txt

Agregar estas líneas:

pdfplumber>=0.11.0
openpyxl>=3.1.0

## PASO 5 — Instalar en el entorno local (PyCharm terminal):

pip install pdfplumber openpyxl

## PASO 6 — Probar localmente

1. Correr: python main.py
2. Abrir: http://localhost:8000/upload_clientes.html
3. Subir un PDF (ej: código de ética)
4. Verificar que aparece en el checklist

## PASO 7 — Verificar endpoints en Swagger

Abrir: http://localhost:8000/docs
Buscar los endpoints nuevos:
  GET  /api/v1/documentos-cliente
  GET  /api/v1/documentos-cliente/tipos
  GET  /api/v1/documentos-cliente/checklist
  POST /api/v1/documentos-cliente/upload
  DELETE /api/v1/documentos-cliente/{tipo}/{nombre_archivo}

## NOTAS

- Los documentos se guardan en data/uploads/{tipo}/
- El registro central está en data/uploads/registro.json
- Sin pdfplumber instalado, igual funciona — solo no extrae texto del PDF
- Sin openpyxl instalado, los XLSX no se procesan (solo se guardan)
- Los archivos .docx se guardan pero no se parsea su contenido (agregar python-docx si querés extracción)

## ESTRUCTURA DE CARPETAS QUE SE CREA

data/
  uploads/
    registro.json          ← índice de todos los documentos
    codigo_etica/
      codigo_conducta.pdf
    nomina_capacitados/
      capacitaciones_2025.xlsx
    listado_proveedores/
      proveedores_activos.csv
    ...
