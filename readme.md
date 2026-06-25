# Canal de Denuncias — Backend

Microservicio FastAPI que da soporte real al Canal de Denuncias del Monitor
de Compliance Empresarial (Ley 27.401). A diferencia del resto del proyecto
`mapa_compliance` (que es estático), este backend persiste datos en una base
real para que el formulario de un denunciante y el panel del compliance
officer puedan verse desde dispositivos distintos.

## Qué hace

- `POST /denuncias` — registrar una denuncia (anónima o identificada). Devuelve un **código de seguimiento** (ej. `DN-2026-A8F3K1`).
- `GET /denuncias/seguimiento/{codigo}` — el propio denunciante consulta el estado con su código. No requiere login. No expone descripción ni datos personales.
- `GET /denuncias` — listado completo (requiere token de compliance).
- `PATCH /denuncias/{codigo}/estado` — actualizar estado y cargar dictamen (requiere token de compliance).
- `GET /denuncias/stats/resumen` — totales por estado/categoría (requiere token de compliance).

## Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `COMPLIANCE_TOKEN` | Sí | Token fijo que debe enviarse en el header `X-Compliance-Token` para acceder a los endpoints de gestión. Elegí un valor largo y aleatorio. |
| `DENUNCIAS_DB_PATH` | No (default `denuncias.db`) | Ruta del archivo SQLite. |

## Deploy en Railway

1. Subí esta carpeta (`main.py` + `requirements.txt`) a un repo nuevo en GitHub, por ejemplo `canal-denuncias`.
2. En Railway: **New Project → Deploy from GitHub repo** → elegí ese repo.
3. En la pestaña **Variables** del servicio, agregá:
   - `COMPLIANCE_TOKEN` = (generá algo largo, ej. con `openssl rand -hex 24`)
4. **Importante — persistencia**: por defecto, el sistema de archivos de Railway se reinicia en cada deploy, así que la base SQLite se perdería. Para que las denuncias no se borren:
   - Andá a la pestaña **Settings** del servicio → **Volumes** → **New Volume**.
   - Montalo en `/app` (o el path donde corra el proyecto) y apuntá `DENUNCIAS_DB_PATH` a un archivo dentro de ese volumen, ej. `/data/denuncias.db`, montando el volumen en `/data`.
5. Railway detecta `requirements.txt` y arranca automáticamente. Si pide un *Start Command*, usá:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. Una vez deployado, copiá la URL pública (ej. `https://canal-denuncias-production.up.railway.app`) — esa es la que se configura en el frontend (`mapa_compliance`) para que el formulario y el tracker le apunten.

## Probar que funciona

```bash
curl https://tu-url-de-railway.up.railway.app/health
# {"status":"healthy","service":"Canal de Denuncias"}
```

## Limitaciones conocidas de esta versión (a tener en cuenta)

- El anonimato es **declarativo**: si la denuncia se marca anónima, el backend no guarda nombre/email aunque lleguen en el request. No se implementa anonimización de IP/metadata de red — quien tenga acceso a los logs del servidor o de Railway podría ver la IP de origen. Si se necesita anonimato técnico real, hay que sumar un proxy/relay adicional.
- Auth de compliance es un token único compartido, no un sistema de usuarios con login individual. Suficiente para un MVP de una sola persona gestionando, pero no para equipos grandes con distintos niveles de acceso.
- Sin envío de notificaciones por email todavía (ni al compliance officer cuando llega una denuncia nueva, ni al denunciante cuando cambia el estado).