from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Importa text para consultas SQL explícitas
import time

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def ping_db(max_retries=3, delay=5):
    """
    Intenta conectar con la base de datos hasta `max_retries` veces.
    :param max_retries: Número máximo de intentos.
    :param delay: Tiempo en segundos entre intentos.
    """
    for attempt in range(max_retries):
        try:
            # Usa text() para declarar explícitamente la consulta SQL
            db.session.execute(text('SELECT 1'))
            return  # Si tiene éxito, salir de la función
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)  # Espera antes de reintentar
            else:
                raise RuntimeError(f"Error al conectar con la base de datos después de {max_retries} intentos: {e}")