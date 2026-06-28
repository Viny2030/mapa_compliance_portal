"""
Onboarding de Clientes — onboarding_cliente.py
Router FastAPI · recibe solicitudes del formulario público,
guarda backup en data/submissions/ y envía emails de notificación.

Emails:
  - ecosistematransparencia@gmail.com  → notificación interna con todos los datos
  - cliente (email ingresado)          → confirmación de recepción
"""

import os
import json
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List

router = APIRouter()

# ── Config SMTP desde .env ────────────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "ecosistematransparencia@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")          # App Password de Gmail
EMAIL_DESTINO = os.getenv("EMAIL_DESTINO", "ecosistematransparencia@gmail.com")

# ── Carpeta de backups ────────────────────────────────────────────────────────
SUBMISSIONS_DIR = Path(__file__).parent.parent / "data" / "submissions"
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)


# ── Modelo de datos ───────────────────────────────────────────────────────────
class SolicitudOnboarding(BaseModel):
    # Datos empresa
    nombre:      str
    cuit:        str
    sector:      str
    tamanio:     str
    pais:        str
    # Contacto
    email:       str
    responsable: Optional[str] = ""
    telefono:    Optional[str] = ""
    # Plan y flags
    plan:        str
    brasil:      bool = False
    ue:          bool = False
    usa:         bool = False
    uk:          bool = False
    bolsa:       bool = False
    tarjetas:    bool = False
    fintech:     bool = False
    sst:         bool = False
    ia:          bool = False
    env:         bool = True
    # Módulos calculados
    modulos:     dict = {}
    # Extras
    mensaje:     Optional[str] = ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _flags_activos(s: SolicitudOnboarding) -> list[str]:
    flags = []
    if s.brasil:   flags.append("Operaciones en Brasil")
    if s.ue:       flags.append("Unión Europea")
    if s.usa:      flags.append("EE.UU. / UK")
    if s.uk:       flags.append("Reino Unido")
    if s.bolsa:    flags.append("Cotiza en bolsa")
    if s.tarjetas: flags.append("Procesamiento de tarjetas")
    if s.fintech:  flags.append("Fintech / Servicios financieros")
    if s.sst:      flags.append("Seguridad y Salud en el Trabajo")
    if s.ia:       flags.append("Inteligencia Artificial")
    if s.env:      flags.append("Gestión ambiental / ESG")
    return flags


def _modulos_activos(modulos: dict) -> list[str]:
    return [k for k, v in modulos.items() if v]


def _guardar_submission(data: SolicitudOnboarding) -> str:
    """Guarda JSON en data/submissions/ y devuelve el ID."""
    submission_id = str(uuid.uuid4())[:8].upper()
    payload = {
        "id":          submission_id,
        "timestamp":   datetime.now().isoformat(),
        **data.model_dump(),
    }
    path = SUBMISSIONS_DIR / f"{submission_id}_{data.nombre[:20].replace(' ','_')}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return submission_id


def _enviar_email(to: str, subject: str, html: str):
    """Envía un email via SMTP. Silencia errores si no hay SMTP configurado."""
    if not SMTP_PASSWORD:
        print(f"[onboarding] SMTP sin contraseña — email a {to} no enviado")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Ecosistema Transparencia <{SMTP_USER}>"
        msg["To"]      = to
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to, msg.as_string())
        print(f"[onboarding] Email enviado a {to}")
    except Exception as e:
        print(f"[onboarding] Error SMTP: {e}")


def _email_interno(s: SolicitudOnboarding, sid: str) -> str:
    flags    = _flags_activos(s)
    modulos  = _modulos_activos(s.modulos)
    plan_map = {"starter": "Starter", "professional": "Professional", "enterprise": "Enterprise"}
    filas_modulos = "".join(
        f"<span style='background:#e3f2fd;padding:2px 8px;border-radius:4px;margin:2px;display:inline-block;font-size:12px'>{m}</span>"
        for m in modulos
    )
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:640px;margin:0 auto;color:#1a1a2e">
      <div style="background:linear-gradient(135deg,#1565c0,#0d47a1);padding:24px 28px;border-radius:10px 10px 0 0">
        <h1 style="color:#fff;margin:0;font-size:20px">🛡️ Nueva Solicitud de Onboarding</h1>
        <p style="color:#bbdefb;margin:4px 0 0;font-size:13px">ID #{sid} · {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
      </div>
      <div style="background:#f8fafc;padding:24px 28px;border:1px solid #e0e7ef;border-top:none;border-radius:0 0 10px 10px">

        <h2 style="font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:#555;border-bottom:1px solid #ddd;padding-bottom:6px">Empresa</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:18px">
          <tr><td style="padding:5px 0;color:#555;width:40%">Nombre</td><td style="font-weight:700">{s.nombre}</td></tr>
          <tr><td style="padding:5px 0;color:#555">CUIT</td><td>{s.cuit}</td></tr>
          <tr><td style="padding:5px 0;color:#555">Sector</td><td>{s.sector.title()}</td></tr>
          <tr><td style="padding:5px 0;color:#555">Tamaño</td><td>{s.tamanio.title()}</td></tr>
          <tr><td style="padding:5px 0;color:#555">País</td><td>{s.pais}</td></tr>
        </table>

        <h2 style="font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:#555;border-bottom:1px solid #ddd;padding-bottom:6px">Contacto</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:18px">
          <tr><td style="padding:5px 0;color:#555;width:40%">Email</td><td><a href="mailto:{s.email}">{s.email}</a></td></tr>
          <tr><td style="padding:5px 0;color:#555">Responsable</td><td>{s.responsable or '—'}</td></tr>
          <tr><td style="padding:5px 0;color:#555">Teléfono</td><td>{s.telefono or '—'}</td></tr>
        </table>

        <h2 style="font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:#555;border-bottom:1px solid #ddd;padding-bottom:6px">Plan & Alcance</h2>
        <p style="margin:6px 0"><strong>Plan:</strong> <span style="background:#1565c0;color:#fff;padding:2px 10px;border-radius:12px;font-size:13px">{plan_map.get(s.plan, s.plan)}</span></p>
        <p style="margin:6px 0"><strong>Flags operacionales:</strong><br>
          {''.join(f'<span style="background:#fff3e0;padding:2px 8px;border-radius:4px;margin:2px;display:inline-block;font-size:12px">✓ {f}</span>' for f in flags) or '<em style="color:#999">Ninguno adicional</em>'}
        </p>
        <p style="margin:10px 0 4px"><strong>Módulos calculados ({len(modulos)}):</strong></p>
        <div>{filas_modulos}</div>

        {"<h2 style='font-size:14px;text-transform:uppercase;letter-spacing:.05em;color:#555;border-bottom:1px solid #ddd;padding-bottom:6px;margin-top:18px'>Mensaje</h2><p style='background:#fff;border-left:3px solid #1565c0;padding:10px 14px;border-radius:0 6px 6px 0'>" + s.mensaje + "</p>" if s.mensaje else ""}

        <div style="margin-top:20px;padding:12px 16px;background:#e8f5e9;border-radius:8px;font-size:13px">
          📌 <strong>Próximo paso:</strong> contactar a {s.responsable or s.nombre} en <a href="mailto:{s.email}">{s.email}</a> para coordinar deploy en Railway y configurar config.js.
        </div>
      </div>
    </div>
    """


def _email_cliente(s: SolicitudOnboarding, sid: str) -> str:
    plan_map = {"starter": "Starter", "professional": "Professional", "enterprise": "Enterprise"}
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a2e">
      <div style="background:linear-gradient(135deg,#1565c0,#0d47a1);padding:28px;border-radius:10px 10px 0 0;text-align:center">
        <h1 style="color:#fff;margin:0;font-size:22px">🛡️ Ecosistema Transparencia</h1>
        <p style="color:#bbdefb;margin:6px 0 0;font-size:14px">Monitor de Compliance Empresarial</p>
      </div>
      <div style="background:#f8fafc;padding:28px;border:1px solid #e0e7ef;border-top:none;border-radius:0 0 10px 10px">
        <p style="font-size:16px">Hola {s.responsable or s.nombre},</p>
        <p>Recibimos tu solicitud para <strong>{s.nombre}</strong>. En las próximas 24–48 horas nos pondremos en contacto para coordinar la configuración de tu plataforma.</p>

        <div style="background:#fff;border:1px solid #e0e7ef;border-radius:8px;padding:16px;margin:20px 0">
          <p style="margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:#888">Resumen de tu solicitud</p>
          <p style="margin:4px 0"><strong>Empresa:</strong> {s.nombre}</p>
          <p style="margin:4px 0"><strong>Plan seleccionado:</strong> {plan_map.get(s.plan, s.plan)}</p>
          <p style="margin:4px 0"><strong>País:</strong> {s.pais}</p>
          <p style="margin:4px 0"><strong>N.° de referencia:</strong> <code style="background:#e3f2fd;padding:1px 6px;border-radius:4px">#{sid}</code></p>
        </div>

        <p>Si tenés preguntas podés responder este email directamente.</p>
        <p style="margin-top:24px">Saludos,<br><strong>Equipo Ecosistema Transparencia</strong><br>
        <a href="mailto:ecosistematransparencia@gmail.com" style="color:#1565c0">ecosistematransparencia@gmail.com</a></p>
      </div>
      <p style="text-align:center;font-size:11px;color:#aaa;margin-top:12px">Ecosistema Transparencia · Ph.D. Vicente H. Monteverde</p>
    </div>
    """


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/onboarding/solicitud", tags=["Onboarding"])
async def recibir_solicitud(data: SolicitudOnboarding):
    """
    Recibe solicitud del formulario público de onboarding.
    - Guarda backup JSON en data/submissions/
    - Envía email interno a ecosistematransparencia@gmail.com
    - Envía email de confirmación al cliente
    """
    # 1. Guardar
    sid = _guardar_submission(data)

    # 2. Email interno
    _enviar_email(
        to      = EMAIL_DESTINO,
        subject = f"🛡️ Nueva solicitud #{sid} — {data.nombre} ({data.plan.title()})",
        html    = _email_interno(data, sid),
    )

    # 3. Email cliente
    _enviar_email(
        to      = data.email,
        subject = f"✅ Recibimos tu solicitud — Ecosistema Transparencia (#{sid})",
        html    = _email_cliente(data, sid),
    )

    return {
        "ok":          True,
        "id":          sid,
        "mensaje":     "Solicitud recibida. Te contactaremos en 24–48 horas.",
        "email_smtp":  bool(SMTP_PASSWORD),
    }


@router.get("/onboarding/submissions", tags=["Onboarding"])
async def listar_submissions():
    """Lista todas las solicitudes guardadas (uso interno)."""
    items = []
    for f in sorted(SUBMISSIONS_DIR.glob("*.json"), reverse=True):
        try:
            items.append(json.loads(f.read_text()))
        except Exception:
            pass
    return {"total": len(items), "submissions": items}