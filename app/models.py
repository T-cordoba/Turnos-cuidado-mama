from .db import db
from datetime import date

class Turno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'día' o 'noche'
    nombre = db.Column(db.String(100), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('fecha', 'tipo', name='_fecha_tipo_uc'),)