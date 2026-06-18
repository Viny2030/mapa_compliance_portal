"""
scheduler.py
Actualización automática semanal de alertas y normativa.
Ejecutable standalone o como proceso background en FastAPI.
"""
import logging
import time
from datetime import datetime

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

INTERVALO_SEGUNDOS = 7 * 24 * 60 * 60  # 1 semana


def correr_etl_completo():
    log.info(f"[{datetime.utcnow().isoformat()}] Iniciando ETL completo ...")
    try:
        from scripts.etl_alertas import correr_etl as etl_alertas
        alertas = etl_alertas()
        log.info(f"  ✓ Alertas: {len(alertas)} registros")
    except Exception as e:
        log.error(f"  ✗ ETL Alertas falló: {e}")

    try:
        from scripts.etl_normativa import correr_etl as etl_normativa
        normas = etl_normativa()
        log.info(f"  ✓ Normativa: {len(normas)} registros")
    except Exception as e:
        log.error(f"  ✗ ETL Normativa falló: {e}")

    log.info("ETL completo finalizado.")


def run_loop():
    """Loop infinito para correr el scheduler en background."""
    log.info("Scheduler iniciado — intervalo: 7 días")
    while True:
        correr_etl_completo()
        log.info(f"Próxima ejecución en {INTERVALO_SEGUNDOS // 3600}h")
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    correr_etl_completo()
