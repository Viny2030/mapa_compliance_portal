"""
Monitor de Compliance Empresarial — main.py
Punto de entrada de la API FastAPI.
Ph.D. Vicente H. Monteverde · Ecosistema Transparencia
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from scripts.api_compliance import router as compliance_router
from scripts.canal_denuncias import router as denuncias_router
from scripts.onboarding_cliente import router as onboarding_router

app = FastAPI(
    title="Monitor de Compliance Empresarial",
    description="API REST — Ley 27.401 · Ley 2/2023 · Estándares Internacionales",
    version="1.1.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────
# ALLOWED_ORIGINS: lista separada por comas en variables de entorno
# (ver .env.example). Si no está seteada, se usa por defecto la lista de
# dominios propios de Railway en vez de "*" — un wildcard combinado con
# endpoints sin auth permite a cualquier sitio invocar la API desde el
# navegador de un visitante y leer la respuesta.
_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _origins_env == "*":
    ALLOWED_ORIGINS = ["*"]
elif _origins_env:
    ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    ALLOWED_ORIGINS = [
        "https://mapacompliance-production.up.railway.app",
        "https://mapatransparencia-production.up.railway.app",
        "https://meaci-production.up.railway.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Session-Token"],
)

# ── Rutas API ───────────────────────────────────────────────────────────────
app.include_router(compliance_router, prefix="/api/v1")
app.include_router(denuncias_router,  prefix="/api/v1", tags=["Canal de Denuncias"])
app.include_router(onboarding_router, prefix="/api/v1", tags=["Onboarding"])

# ── Archivos estáticos (frontend) ───────────────────────────────────────────
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

# ── Archivos raíz (HTMLs + config.js) ───────────────────────────────────────
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
    return FileResponse(os.path.join(ROOT, "canal_denuncias.html"))

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

@app.get("/formulario-cliente.html", include_in_schema=False)
async def formulario_cliente_html():
    return FileResponse(os.path.join(ROOT, "formulario-cliente.html"))

@app.get("/onboarding.html", include_in_schema=False)
async def onboarding_html():
    return FileResponse(os.path.join(ROOT, "onboarding.html"))

@app.get("/portal.html", include_in_schema=False)
async def portal_html():
    return FileResponse(os.path.join(ROOT, "portal.html"))

@app.get("/bridge.html", include_in_schema=False)
async def bridge_html():
    return FileResponse(os.path.join(ROOT, "bridge.html"))
# ── Catch-all para HTMLs sueltos en la raíz (incluye -en/-fr/-pt) ──────────
from fastapi import HTTPException

@app.get("/{filename}.html", include_in_schema=False)
async def serve_any_html(filename: str):
    path = os.path.join(ROOT, f"{filename}.html")
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
