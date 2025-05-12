from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Importa text para consultas SQL explícitas
from sqlalchemy.exc import OperationalError
from time import sleep
import time

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def ping_db(max_retries=3, delay=2):
    """
    Verifica si la base de datos está activa. Si está suspendida, intenta reconectarse.
    """
    for intento in range(max_retries):
        try:
            # Realiza una consulta simple para verificar la conexión
            db.session.execute(text('SELECT 1'))  # Usa text() para envolver la consulta
            return True  # Conexión exitosa
        except OperationalError:
            print(f"Intento {intento + 1} de {max_retries}: La base de datos está suspendida. Reintentando...")
            sleep(delay)  # Espera antes de intentar nuevamente
    # Si todos los intentos fallan, lanza un RuntimeError
    raise RuntimeError("No se pudo establecer conexión con la base de datos después de varios intentos.")