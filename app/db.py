from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Importa text para consultas SQL explícitas
from sqlalchemy.exc import OperationalError, PendingRollbackError
from time import sleep
import time

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def ping_db(delay=2):
    """
    Verifica si la base de datos está activa. Reintenta indefinidamente hasta que esté disponible.
    """
    while True:
        try:
            # Realiza una consulta simple para verificar la conexión
            db.session.execute(text('SELECT 1'))  # Usa text() para envolver la consulta
            return True  # Conexión exitosa
        except PendingRollbackError:
            # Si hay una transacción pendiente, realiza un rollback
            print("Transacción inválida detectada. Realizando rollback...")
            db.session.rollback()
        except OperationalError:
            # Si la base de datos está suspendida, espera y reintenta
            print("La base de datos está suspendida. Reintentando...")
            sleep(delay)  # Espera antes de intentar nuevamente