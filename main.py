"""
Monitor de Compliance Empresarial â main.py
Punto de entrada de la API FastAPI.
Ph.D. Vicente H. Monteverde Â· Ecosistema Transparencia
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from scripts.api_compliance import router as compliance_router
from scripts.canal_denuncias import router as denuncias_router

app = FastAPI(
    title="Monitor de Compliance Empresarial",
    description="API REST â Ley 27.401 Â· Ley 2/2023 Â· EstÃ¡ndares Internacionales",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ââ Rutas API âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
app.include_router(compliance_router, prefix="/api/v1")
app.include_router(denuncias_router,  prefix="/api/v1", tags=["Canal de Denuncias"])

# ââ Archivos estÃ¡ticos (frontend) âââââââââââââââââââââââââââââââââââââââââââ
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def root():
    index = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "ok", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.1.0"}

# ââ Archivos raÃ­z (HTMLs + config.js) âââââââââââââââââââââââââââââââââââââââ
ROOT = os.path.dirname(__file__)

@app.get("/index.html", include_in_schema=False)
async def index_html():
    return FileResponse(os.path.join(ROOT, "index.html"))

@app.get("/config.js", include_in_schema=False)
async def config_js():
    return FileResponse(os.path.join(ROOT, "config.js"))

@app.get("/config.demo.js", include_in_schema=False)
async def config_demo_js():
    return FileResponse(os.path.join(ROOT, "config.demo.js"))

@app.get("/canal_denuncias.html", include_in_schema=False)
async def canal_denuncias_html():
    return FileResponse(os.path.join(os.path.dirname(__file__), "canal_denuncias.html"))

@app.get("/benchmark.html", include_in_schema=False)
async def benchmark_html():
    return FileResponse(os.path.join(ROOT, "benchmark.html"))

@app.get("/documentos.html", include_in_schema=False)
async def documentos_html():
    return FileResponse(os.path.join(ROOT, "documentos.html"))

@app.get("/landing.html", include_in_schema=False)
async def landing_html():
    return FileResponse(os.path.join(ROOT, "landing.html"))

@app.get("/conflicto_interes.html", include_in_schema=False)
async def conflicto_interes_html():
    return FileResponse(os.path.join(ROOT, "conflicto_interes.html"))

@app.get("/incidentes.html", include_in_schema=False)
async def incidentes_html():
    return FileResponse(os.path.join(ROOT, "incidentes.html"))

@app.get("/controles.html", include_in_schema=False)
async def controles_html():
    return FileResponse(os.path.join(ROOT, "controles.html"))

@app.get("/predictor.html", include_in_schema=False)
async def predictor_html():
    return FileResponse(os.path.join(ROOT, "predictor.html"))

@app.get("/capacitaciones.html", include_in_schema=False)
async def capacitaciones_html():
    return FileResponse(os.path.join(ROOT, "capacitaciones.html"))

@app.get("/upload_clientes.html", include_in_schema=False)
async def upload_clientes_html():
    return FileResponse(os.path.join(ROOT, "upload_clientes.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
