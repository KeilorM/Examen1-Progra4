from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import SessionLocal
from app.services.paciente_service import hacer_imagenes_privadas

def ejecutar_tarea_privacidad():
    db = SessionLocal()
    try:
        print("Ejecutando tarea: ocultando imágenes...")
        hacer_imagenes_privadas(db)
        print("Tarea completada ✅")
    except Exception as e:
        print(f"Error en tarea programada: {e}")
    finally:
        db.close()

def iniciar_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        ejecutar_tarea_privacidad,
        CronTrigger(minute="*/2"),
        #CronTrigger(hour=23, minute=59),
        id="ocultar_imagenes",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler iniciado ✅ - Tarea a las 23:59")
    return scheduler