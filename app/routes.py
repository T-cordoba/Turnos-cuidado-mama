import locale
from flask import Blueprint, render_template, request, redirect, url_for, Flask, Response, flash
from datetime import datetime, timedelta
from .models import Turno
from .db import db

app = Flask(__name__)

@app.after_request
def set_charset(response):
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        tipo = request.form['tipo']
        action = request.form['action']

        if action == 'reservar':
            nombre = request.form['nombre'].strip()
            turno = Turno(fecha=fecha, tipo=tipo, nombre=nombre)
            db.session.add(turno)
            try:
                db.session.commit()
                flash(f"Reserva realizada con éxito para {nombre} el {fecha.strftime('%d/%m/%Y')} en el turno {tipo}.", "success")
            except:
                db.session.rollback()
                flash("Ocurrió un error al realizar la reserva. Inténtalo nuevamente.", "error")
        elif action == 'cancelar':
            turno = Turno.query.filter_by(fecha=fecha, tipo=tipo).first()
            if turno:
                nombre = turno.nombre
                Turno.query.filter_by(fecha=fecha, tipo=tipo).delete()
                db.session.commit()
                flash(f"Reserva de {nombre} cancelada con éxito para el {fecha.strftime('%d/%m/%Y')} en el turno {tipo}.", "success")
            else:
                flash("No se encontró la reserva para cancelar.", "error")

        return redirect(url_for('main.index'))

    locale.setlocale(locale.LC_TIME, 'C')

    hoy = datetime.today().date()
    dia_semana_hoy = hoy.weekday()  # 0 = Lunes, 6 = Domingo

    # Calcular el domingo de la semana actual
    domingo_actual = hoy + timedelta(days=(6 - dia_semana_hoy))

    # Días de la semana actual (desde hoy hasta el domingo)
    dias_semana_actual = [hoy + timedelta(days=i) for i in range((domingo_actual - hoy).days + 1)]

    # Calcular el lunes y domingo de la próxima semana
    lunes_proxima_semana = domingo_actual + timedelta(days=1)
    domingo_proxima_semana = lunes_proxima_semana + timedelta(days=6)

    # Días de la próxima semana (lunes a domingo)
    dias_proxima_semana = [lunes_proxima_semana + timedelta(days=i) for i in range(7)]

    # Traducir los días
    dias_traducidos = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    # Crear turnos
    turnos = {(t.fecha, t.tipo): t.nombre for t in Turno.query.all()}

    return render_template(
        'index.html',
        dias_semana_actual=[(dia, dia.strftime('%A')) for dia in dias_semana_actual],
        dias_proxima_semana=[(dia, dia.strftime('%A')) for dia in dias_proxima_semana],
        turnos=turnos,
        dias_traducidos=dias_traducidos,
        hoy=hoy
    )
