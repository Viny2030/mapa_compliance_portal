"""
main.py — Portal multi-empresa
Agrega sobre el main original:
  - Login con sesión (cookie)
  - API /api/clientes  → lista clientes del consultor
  - API /api/cliente/{id}/config → devuelve el config.js del cliente
  - Página /portal → selector de clientes
"""
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
import uvicorn, os, json, hashlib, secrets
from pathlib import Path
from datetime import datetime, timezone

# ── Rutas del proyecto ────────────────────────────────────────────────────────
ROOT      = Path(__file__).parent
DATA_DIR  = ROOT / "data"
CLIENTES_FILE = DATA_DIR / "clientes.json"
SESIONES: dict[str, dict] = {}   # token → {consultor_id, expires}

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Portal Compliance — Multi-empresa", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Archivos estáticos
if (ROOT / "static").exists():
    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

# ── Helpers ───────────────────────────────────────────────────────────────────
def _cargar_db() -> dict:
    if CLIENTES_FILE.exists():
        return json.loads(CLIENTES_FILE.read_text(encoding="utf-8"))
    return {"consultores": [], "clientes": []}

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def _get_sesion(request: Request) -> dict | None:
    token = request.cookies.get("portal_token")
    if not token or token not in SESIONES:
        return None
    return SESIONES[token]

def _require_login(request: Request) -> dict:
    sesion = _get_sesion(request)
    if not sesion:
        raise HTTPException(status_code=401, detail="No autenticado")
    return sesion

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.post("/api/login")
async def login(request: Request, response: Response):
    data = await request.json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    db = _cargar_db()
    consultor = next(
        (c for c in db.get("consultores", [])
         if c["email"].lower() == email and c["password_hash"] == _hash(password)),
        None,
    )
    if not consultor:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = secrets.token_hex(32)
    SESIONES[token] = {
        "consultor_id": consultor["id"],
        "nombre":       consultor["nombre"],
        "clientes":     consultor.get("clientes", []),
    }
    response = JSONResponse({"ok": True, "nombre": consultor["nombre"]})
    response.set_cookie("portal_token", token, httponly=True, samesite="lax", max_age=28800)
    return response

@app.post("/api/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get("portal_token")
    if token in SESIONES:
        del SESIONES[token]
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("portal_token")
    return resp

@app.get("/api/me")
async def me(request: Request):
    sesion = _get_sesion(request)
    if not sesion:
        return JSONResponse({"autenticado": False})
    return JSONResponse({"autenticado": True, "nombre": sesion["nombre"]})

# ── Clientes ──────────────────────────────────────────────────────────────────
@app.get("/api/clientes")
async def listar_clientes(request: Request):
    sesion = _require_login(request)
    db = _cargar_db()
    ids_permitidos = sesion["clientes"]
    clientes = [
        c for c in db.get("clientes", [])
        if c["id"] in ids_permitidos and c.get("activo", True)
    ]
    return JSONResponse(clientes)

@app.get("/api/cliente/{cliente_id}/config")
async def config_cliente(cliente_id: str, request: Request):
    sesion = _require_login(request)
    if cliente_id not in sesion["clientes"]:
        raise HTTPException(status_code=403, detail="Sin acceso a este cliente")
    db = _cargar_db()
    cliente = next((c for c in db["clientes"] if c["id"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    # Devolver config.js personalizado para este cliente
    config_path = DATA_DIR / "clientes" / cliente_id / "config.js"
    if config_path.exists():
        return FileResponse(config_path, media_type="application/javascript")
    # Fallback: config.js base con datos del cliente inyectados
    config_base = (ROOT / "config.js").read_text(encoding="utf-8")
    config_base = config_base.replace(
        'nombre_empresa: "Empresa Demo S.A."',
        f'nombre_empresa: "{cliente["nombre"]}"'
    ).replace(
        'pais: "AR"',
        f'pais: "{cliente.get("pais","AR")}"'
    )
    return Response(content=config_base, media_type="application/javascript")

@app.post("/api/cliente")
async def crear_cliente(request: Request):
    """Agrega un nuevo cliente al consultor autenticado."""
    sesion = _require_login(request)
    data = await request.json()
    db = _cargar_db()
    nuevo_id = f"c{len(db['clientes'])+1:03d}"
    nuevo = {
        "id":     nuevo_id,
        "nombre": data.get("nombre", "Sin nombre"),
        "cuit":   data.get("cuit", ""),
        "pais":   data.get("pais", "AR"),
        "sector": data.get("sector", ""),
        "activo": True,
    }
    db["clientes"].append(nuevo)
    # Asignar al consultor actual
    for c in db["consultores"]:
        if c["id"] == sesion["consultor_id"]:
            c.setdefault("clientes", []).append(nuevo_id)
            sesion["clientes"].append(nuevo_id)
            break
    # Crear carpeta del cliente
    (DATA_DIR / "clientes" / nuevo_id).mkdir(parents=True, exist_ok=True)
    CLIENTES_FILE.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    return JSONResponse({"ok": True, "id": nuevo_id})

# ── Páginas ───────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root(request: Request):
    sesion = _get_sesion(request)
    if not sesion:
        return FileResponse(ROOT / "portal_login.html")
    return FileResponse(ROOT / "portal_clientes.html")

@app.get("/portal", include_in_schema=False)
async def portal(request: Request):
    sesion = _get_sesion(request)
    if not sesion:
        return RedirectResponse("/")
    return FileResponse(ROOT / "portal_clientes.html")

@app.get("/dashboard/{cliente_id}", include_in_schema=False)
async def dashboard_cliente(cliente_id: str, request: Request):
    sesion = _get_sesion(request)
    if not sesion:
        return RedirectResponse("/")
    if cliente_id not in sesion["clientes"]:
        raise HTTPException(status_code=403)
    return FileResponse(ROOT / "index.html")

# Servir todos los demás HTML
for _html in ["index","canal_denuncias","benchmark","documentos","landing",
              "conflicto_interes","incidentes","controles","predictor",
              "capacitaciones","upload_clientes"]:
    def _make_route(name):
        @app.get(f"/{name}.html", include_in_schema=False)
        async def _route():
            return FileResponse(ROOT / f"{name}.html")
    _make_route(_html)

@app.get("/config.js", include_in_schema=False)
async def config_js(request: Request, cliente: str = ""):
    """Sirve config.js del cliente activo (query param ?cliente=c001)."""
    sesion = _get_sesion(request)
    if sesion and cliente and cliente in sesion["clientes"]:
        config_path = DATA_DIR / "clientes" / cliente / "config.js"
        if config_path.exists():
            return FileResponse(config_path, media_type="application/javascript")
    return FileResponse(ROOT / "config.js", media_type="application/javascript")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "modulo": "portal-multiempresa"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

