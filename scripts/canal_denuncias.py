"""
Canal de Denuncias â canal_denuncias.py
Router FastAPI Â· SQLite Â· Ley 2/2023 (EspaÃ±a) / Ley 27.401 (Argentina)
Ph.D. Vicente H. Monteverde Â· Ecosistema Transparencia

Sistema de PINs con expiraciÃ³n:
  - PIN_CONSULTOR: definido en .env â acceso total
  - PIN_COMPLIANCE: definido en .env â acceso total
  - Ambos PINs tienen fecha de expiraciÃ³n configurable
  - Las sesiones duran SESSION_HOURS (default 8 hs)
"""
import sqlite3
import uuid
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel

router = APIRouter()

# ââ ConfiguraciÃ³n de PINs desde .env ââââââââââââââââââââââââââââââââââââââââ
# En .env agregar:
#   PIN_CONSULTOR=1234
#   PIN_COMPLIANCE=5678
#   PIN_EXPIRA_DIAS=30        (el PIN en sÃ­ expira cada N dÃ­as, default 30)
#   SESSION_HOURS=8           (cada sesiÃ³n dura N horas, default 8)

PIN_CONSULTOR   = os.getenv("PIN_CONSULTOR", "0000")
PIN_COMPLIANCE  = os.getenv("PIN_COMPLIANCE", "1111")
PIN_EXPIRA_DIAS = int(os.getenv("PIN_EXPIRA_DIAS", "30"))
SESSION_HOURS   = int(os.getenv("SESSION_HOURS", "8"))

# Tokens de sesiÃ³n activos en memoria {token: {rol, expira}}
_sesiones: dict = {}


# ââ Base de datos ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "denuncias.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS denuncias (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_seguimiento    TEXT UNIQUE NOT NULL,
        categoria             TEXT NOT NULL,
        descripcion           TEXT NOT NULL,
        es_anonima            INTEGER NOT NULL DEFAULT 1,
        datos_contacto        TEXT,
        estado                TEXT NOT NULL DEFAULT 'recibida',
        prioridad             TEXT NOT NULL DEFAULT 'media',
        area_relacionada      TEXT,
        fecha_creacion        TEXT NOT NULL,
        fecha_limite_acuse    TEXT NOT NULL,
        fecha_limite_cierre   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS actualizaciones (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        denuncia_id  INTEGER NOT NULL,
        mensaje      TEXT NOT NULL,
        fecha        TEXT NOT NULL,
        autor        TEXT NOT NULL DEFAULT 'denunciante',
        FOREIGN KEY (denuncia_id) REFERENCES denuncias(id)
    );

    CREATE TABLE IF NOT EXISTS alertas (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        denuncia_id     INTEGER NOT NULL,
        tipo            TEXT NOT NULL,
        fecha_generada  TEXT NOT NULL,
        leida           INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (denuncia_id) REFERENCES denuncias(id)
    );

    CREATE TABLE IF NOT EXISTS sesiones_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        rol         TEXT NOT NULL,
        ip          TEXT,
        fecha       TEXT NOT NULL,
        accion      TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()


init_db()


# ââ Schemas Pydantic âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
class DenunciaCreate(BaseModel):
    categoria: str
    descripcion: str
    es_anonima: bool = True
    datos_contacto: Optional[str] = None
    area_relacionada: Optional[str] = None
    prioridad: str = "media"


class DenunciaUpdate(BaseModel):
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    area_relacionada: Optional[str] = None


class MensajeSeguimiento(BaseModel):
    mensaje: str
    autor: str = "denunciante"


class LoginRequest(BaseModel):
    pin: str


# ââ Auth helpers âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def _pin_expirado() -> bool:
    """Verifica si los PINs actuales superaron su vida Ãºtil."""
    # Usamos el archivo .env mtime como referencia de cuÃ¡ndo se configuraron
    # Si no existe referencia, asumimos que son vÃ¡lidos (primera vez)
    ref_file = os.path.join(os.path.dirname(__file__), "..", "data", "pin_fecha.txt")
    if not os.path.exists(ref_file):
        # Crear referencia con fecha actual
        with open(ref_file, "w") as f:
            f.write(datetime.utcnow().isoformat())
        return False
    with open(ref_file) as f:
        fecha_str = f.read().strip()
    try:
        fecha_set = datetime.fromisoformat(fecha_str)
        return (datetime.utcnow() - fecha_set).days >= PIN_EXPIRA_DIAS
    except Exception:
        return False


def _renovar_fecha_pin():
    """Actualiza la fecha de referencia del PIN (al cambiar desde .env)."""
    ref_file = os.path.join(os.path.dirname(__file__), "..", "data", "pin_fecha.txt")
    with open(ref_file, "w") as f:
        f.write(datetime.utcnow().isoformat())


def _nueva_sesion(rol: str) -> str:
    """Genera un token de sesiÃ³n con expiraciÃ³n."""
    token = secrets.token_urlsafe(32)
    expira = datetime.utcnow() + timedelta(hours=SESSION_HOURS)
    _sesiones[token] = {"rol": rol, "expira": expira}
    return token


def _validar_token(token: str) -> dict:
    """Valida el token y devuelve {rol}. Lanza 401 si invÃ¡lido o expirado."""
    if not token:
        raise HTTPException(status_code=401, detail="Token requerido. IniciÃ¡ sesiÃ³n primero.")
    sesion = _sesiones.get(token)
    if not sesion:
        raise HTTPException(status_code=401, detail="SesiÃ³n invÃ¡lida o expirada.")
    if datetime.utcnow() > sesion["expira"]:
        del _sesiones[token]
        raise HTTPException(status_code=401, detail="SesiÃ³n expirada. VolvÃ© a ingresar el PIN.")
    return sesion


def _log_sesion(rol: str, accion: str):
    """Registra accesos en la BD para auditorÃ­a."""
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO sesiones_log (rol, fecha, accion) VALUES (?,?,?)",
            (rol, _ahora(), accion)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# ââ Helpers generales âââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
def _codigo_corto() -> str:
    return str(uuid.uuid4()).replace("-", "")[:8].upper()


def _ahora() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def _generar_alertas_si_procede(conn, denuncia_id: int, denuncia: dict):
    ahora = datetime.utcnow()
    acuse = datetime.fromisoformat(denuncia["fecha_limite_acuse"].rstrip("Z"))
    cierre = datetime.fromisoformat(denuncia["fecha_limite_cierre"].rstrip("Z"))

    def _existe_alerta(tipo: str) -> bool:
        r = conn.execute(
            "SELECT id FROM alertas WHERE denuncia_id=? AND tipo=?",
            (denuncia_id, tipo)
        ).fetchone()
        return r is not None

    if ahora > acuse and denuncia["estado"] == "recibida":
        if not _existe_alerta("plazo_acuse_vencido"):
            conn.execute(
                "INSERT INTO alertas (denuncia_id, tipo, fecha_generada) VALUES (?,?,?)",
                (denuncia_id, "plazo_acuse_vencido", _ahora())
            )

    if timedelta(0) < (cierre - ahora) <= timedelta(days=10):
        if not _existe_alerta("plazo_respuesta_proximo"):
            conn.execute(
                "INSERT INTO alertas (denuncia_id, tipo, fecha_generada) VALUES (?,?,?)",
                (denuncia_id, "plazo_respuesta_proximo", _ahora())
            )

    if denuncia["prioridad"] == "alta" and denuncia["estado"] == "en_investigacion":
        creacion = datetime.fromisoformat(denuncia["fecha_creacion"].rstrip("Z"))
        if (ahora - creacion).days > 30:
            if not _existe_alerta("caso_critico"):
                conn.execute(
                    "INSERT INTO alertas (denuncia_id, tipo, fecha_generada) VALUES (?,?,?)",
                    (denuncia_id, "caso_critico", _ahora())
                )


# ââ Endpoints de autenticaciÃ³n âââââââââââââââââââââââââââââââââââââââââââââââ

@router.post("/denuncias/auth/login", summary="Login con PIN")
def login(body: LoginRequest):
    """
    IngresÃ¡ el PIN de consultor o compliance officer.
    Devuelve un token de sesiÃ³n vÃ¡lido por SESSION_HOURS horas.
    """
    if _pin_expirado():
        raise HTTPException(
            status_code=403,
            detail=f"Los PINs expiraron. ActualizÃ¡ PIN_CONSULTOR y PIN_COMPLIANCE en el .env y reiniciÃ¡ el servidor."
        )

    if body.pin == PIN_CONSULTOR:
        token = _nueva_sesion("consultor")
        _log_sesion("consultor", "login")
        expira = (_sesiones[token]["expira"]).isoformat()
        return {
            "ok": True,
            "rol": "consultor",
            "token": token,
            "expira": expira,
            "session_hours": SESSION_HOURS,
        }
    elif body.pin == PIN_COMPLIANCE:
        token = _nueva_sesion("compliance")
        _log_sesion("compliance", "login")
        expira = (_sesiones[token]["expira"]).isoformat()
        return {
            "ok": True,
            "rol": "compliance",
            "token": token,
            "expira": expira,
            "session_hours": SESSION_HOURS,
        }
    else:
        _log_sesion("desconocido", "login_fallido")
        raise HTTPException(status_code=401, detail="PIN incorrecto.")


@router.post("/denuncias/auth/logout", summary="Cerrar sesiÃ³n")
def logout(x_session_token: str = Header(...)):
    """Invalida el token de sesiÃ³n actual."""
    if x_session_token in _sesiones:
        rol = _sesiones[x_session_token]["rol"]
        del _sesiones[x_session_token]
        _log_sesion(rol, "logout")
    return {"ok": True, "mensaje": "SesiÃ³n cerrada."}


@router.get("/denuncias/auth/estado", summary="Verificar estado de sesiÃ³n")
def estado_sesion(x_session_token: str = Header(...)):
    """Verifica si el token sigue activo y devuelve el rol."""
    sesion = _validar_token(x_session_token)
    minutos_restantes = int((sesion["expira"] - datetime.utcnow()).total_seconds() / 60)
    return {
        "activa": True,
        "rol": sesion["rol"],
        "expira": sesion["expira"].isoformat(),
        "minutos_restantes": minutos_restantes,
        "pin_expira_en_dias": max(0, PIN_EXPIRA_DIAS - (
            datetime.utcnow() - datetime.fromisoformat(
                open(os.path.join(os.path.dirname(__file__), "..", "data", "pin_fecha.txt")).read().strip()
            )
        ).days) if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "data", "pin_fecha.txt")) else PIN_EXPIRA_DIAS,
    }


# ââ Endpoints pÃºblicos (sin auth) ââââââââââââââââââââââââââââââââââââââââââââ

@router.post("/denuncias", summary="Crear denuncia (pÃºblico)")
def crear_denuncia(body: DenunciaCreate):
    """Crea una denuncia. No requiere autenticaciÃ³n."""
    if not body.es_anonima and not body.datos_contacto:
        raise HTTPException(
            status_code=422,
            detail="datos_contacto es obligatorio cuando la denuncia no es anÃ³nima."
        )

    ahora = datetime.utcnow()
    codigo = _codigo_corto()
    fecha_creacion = ahora.isoformat(timespec="seconds") + "Z"
    fecha_limite_acuse = (ahora + timedelta(days=7)).isoformat(timespec="seconds") + "Z"
    fecha_limite_cierre = (ahora + timedelta(days=90)).isoformat(timespec="seconds") + "Z"
    contacto = body.datos_contacto if not body.es_anonima else None

    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO denuncias
               (codigo_seguimiento, categoria, descripcion, es_anonima, datos_contacto,
                prioridad, area_relacionada, fecha_creacion, fecha_limite_acuse, fecha_limite_cierre)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (codigo, body.categoria, body.descripcion, int(body.es_anonima),
             contacto, body.prioridad, body.area_relacionada,
             fecha_creacion, fecha_limite_acuse, fecha_limite_cierre)
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "mensaje": "Denuncia registrada correctamente.",
        "codigo_seguimiento": codigo,
        "fecha_limite_acuse": fecha_limite_acuse,
        "fecha_limite_cierre": fecha_limite_cierre,
        "aviso": "Guarde este cÃ³digo. Es la Ãºnica forma de consultar su caso."
    }


@router.get("/denuncias/seguimiento/{codigo}", summary="Consultar caso por cÃ³digo (pÃºblico)")
def consultar_seguimiento(codigo: str):
    """El denunciante consulta el estado de su caso con el cÃ³digo de seguimiento."""
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM denuncias WHERE codigo_seguimiento=?",
            (codigo.upper(),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="CÃ³digo de seguimiento no encontrado.")

        denuncia = _row_to_dict(row)
        denuncia.pop("datos_contacto", None)

        actualizaciones = [
            _row_to_dict(r) for r in conn.execute(
                "SELECT id, mensaje, fecha, autor FROM actualizaciones WHERE denuncia_id=? ORDER BY fecha DESC",
                (denuncia["id"],)
            ).fetchall()
        ]
    finally:
        conn.close()

    return {
        "denuncia": denuncia,
        "actualizaciones": actualizaciones,
        "total_mensajes": len(actualizaciones)
    }


@router.post("/denuncias/seguimiento/{codigo}/mensaje", summary="Agregar mensaje al caso (pÃºblico)")
def agregar_mensaje_seguimiento(codigo: str, body: MensajeSeguimiento):
    """El denunciante agrega informaciÃ³n al caso."""
    if body.autor not in ("denunciante", "compliance"):
        raise HTTPException(status_code=422, detail="autor debe ser 'denunciante' o 'compliance'.")

    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id FROM denuncias WHERE codigo_seguimiento=?",
            (codigo.upper(),)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="CÃ³digo de seguimiento no encontrado.")

        conn.execute(
            "INSERT INTO actualizaciones (denuncia_id, mensaje, fecha, autor) VALUES (?,?,?,?)",
            (row["id"], body.mensaje, _ahora(), body.autor)
        )
        conn.commit()
    finally:
        conn.close()

    return {"mensaje": "Mensaje agregado correctamente.", "codigo": codigo.upper()}


# ââ Endpoints de gestiÃ³n â REQUIEREN TOKEN âââââââââââââââââââââââââââââââââââ

@router.get("/denuncias", summary="Listar todas las denuncias (panel â requiere PIN)")
def listar_denuncias(
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    x_session_token: str = Header(...),
):
    """Panel de gestiÃ³n. Requiere token de sesiÃ³n en header X-Session-Token."""
    sesion = _validar_token(x_session_token)
    _log_sesion(sesion["rol"], "listar_denuncias")

    filters, params = [], []
    if estado:
        filters.append("estado = ?"); params.append(estado)
    if prioridad:
        filters.append("prioridad = ?"); params.append(prioridad)
    if categoria:
        filters.append("categoria = ?"); params.append(categoria)
    if area:
        filters.append("area_relacionada = ?"); params.append(area)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    query = f"SELECT * FROM denuncias {where} ORDER BY fecha_creacion DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    conn = get_conn()
    try:
        rows = conn.execute(query, params).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM denuncias {where}", params[:-2]
        ).fetchone()[0]

        denuncias = []
        for row in rows:
            d = _row_to_dict(row)
            _generar_alertas_si_procede(conn, d["id"], d)
            denuncias.append(d)
        conn.commit()
    finally:
        conn.close()

    return {"total": total, "limit": limit, "offset": offset, "denuncias": denuncias}


@router.patch("/denuncias/{id}", summary="Actualizar estado/prioridad (panel â requiere PIN)")
def actualizar_denuncia(
    id: int,
    body: DenunciaUpdate,
    x_session_token: str = Header(...),
):
    """Cambia estado, prioridad o Ã¡rea. Requiere token."""
    sesion = _validar_token(x_session_token)
    _log_sesion(sesion["rol"], f"actualizar_denuncia_{id}")

    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM denuncias WHERE id=?", (id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Denuncia no encontrada.")

        updates = {}
        if body.estado:
            validos = ("recibida", "en_investigacion", "cerrada")
            if body.estado not in validos:
                raise HTTPException(status_code=422, detail=f"estado debe ser uno de: {validos}")
            updates["estado"] = body.estado
        if body.prioridad:
            validos_p = ("alta", "media", "baja")
            if body.prioridad not in validos_p:
                raise HTTPException(status_code=422, detail=f"prioridad debe ser uno de: {validos_p}")
            updates["prioridad"] = body.prioridad
        if body.area_relacionada is not None:
            updates["area_relacionada"] = body.area_relacionada

        if not updates:
            raise HTTPException(status_code=422, detail="Nada que actualizar.")

        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(
            f"UPDATE denuncias SET {set_clause} WHERE id=?",
            list(updates.values()) + [id]
        )
        if body.estado == "cerrada":
            conn.execute(
                "INSERT INTO actualizaciones (denuncia_id, mensaje, fecha, autor) VALUES (?,?,?,?)",
                (id, "Caso cerrado por el equipo de compliance.", _ahora(), "compliance")
            )
        conn.commit()
        updated = _row_to_dict(conn.execute("SELECT * FROM denuncias WHERE id=?", (id,)).fetchone())
    finally:
        conn.close()

    return {"mensaje": "Denuncia actualizada.", "denuncia": updated}


@router.get("/denuncias/alertas", summary="Alertas activas (panel â requiere PIN)")
def listar_alertas(
    solo_no_leidas: bool = Query(True),
    x_session_token: str = Header(...),
):
    """Alertas activas. Requiere token."""
    _validar_token(x_session_token)

    conn = get_conn()
    try:
        where = "WHERE a.leida = 0" if solo_no_leidas else ""
        rows = conn.execute(
            f"""SELECT a.*, d.codigo_seguimiento, d.categoria, d.estado, d.prioridad, d.area_relacionada
                FROM alertas a
                JOIN denuncias d ON a.denuncia_id = d.id
                {where}
                ORDER BY a.fecha_generada DESC""",
        ).fetchall()
        alertas = [_row_to_dict(r) for r in rows]
    finally:
        conn.close()

    return {"total": len(alertas), "alertas": alertas}


@router.patch("/denuncias/alertas/{id}/leer", summary="Marcar alerta como leÃ­da (requiere PIN)")
def marcar_alerta_leida(id: int, x_session_token: str = Header(...)):
    _validar_token(x_session_token)
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM alertas WHERE id=?", (id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Alerta no encontrada.")
        conn.execute("UPDATE alertas SET leida=1 WHERE id=?", (id,))
        conn.commit()
    finally:
        conn.close()
    return {"mensaje": "Alerta marcada como leÃ­da.", "id": id}


@router.get("/denuncias/resumen/por-area", summary="Resumen por Ã¡rea (requiere PIN)")
def resumen_por_area(x_session_token: str = Header(...)):
    _validar_token(x_session_token)
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT area_relacionada,
                COUNT(*) as total,
                SUM(CASE WHEN estado='recibida' THEN 1 ELSE 0 END) as recibidas,
                SUM(CASE WHEN estado='en_investigacion' THEN 1 ELSE 0 END) as en_investigacion,
                SUM(CASE WHEN estado='cerrada' THEN 1 ELSE 0 END) as cerradas,
                SUM(CASE WHEN prioridad='alta' THEN 1 ELSE 0 END) as alta_prioridad
               FROM denuncias
               GROUP BY area_relacionada
               ORDER BY total DESC"""
        ).fetchall()
    finally:
        conn.close()

    return {"resumen": [_row_to_dict(r) for r in rows]}
