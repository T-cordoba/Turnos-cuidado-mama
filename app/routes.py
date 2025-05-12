import locale
from flask import Blueprint, render_template, request, redirect, url_for, Flask, Response, flash
from datetime import datetime, timedelta
from .models import Turno
from .db import db, ping_db

app = Flask(__name__)

@app.after_request
def set_charset(response):
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    # Verifica la conexión con la base de datos
    ping_db()

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

            # Redirige con el parámetro scrollToTop
            return redirect(url_for('main.index', scrollToTop='true'))

        return redirect(url_for('main.index'))

    hoy = datetime.today().date()

    # Crear turnos (debe estar definido antes de calcular los turnos faltantes)
    turnos = {(t.fecha, t.tipo): t.nombre for t in Turno.query.all()}

    # Traducción de días al español
    dias_traducidos = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    # Calcular los próximos 3 días
    proximos_3_dias = [hoy + timedelta(days=i) for i in range(3)]

    # Obtener los turnos faltantes para los próximos 3 días
    turnos_faltantes = []
    for dia in proximos_3_dias:
        for turno in ['día', 'noche']:
            if (dia, turno) not in turnos:
                turnos_faltantes.append({
                    'fecha': dia.strftime('%d/%m/%Y'),
                    'tipo': turno,
                    'dia': dias_traducidos[dia.strftime('%A')]  # Traduce el día al español aquí
                })

    # Calcular los días de la semana actual y próxima semana
    dia_semana_hoy = hoy.weekday()  # 0 = Lunes, 6 = Domingo
    domingo_actual = hoy + timedelta(days=(6 - dia_semana_hoy))
    dias_semana_actual = [hoy + timedelta(days=i) for i in range((domingo_actual - hoy).days + 1)]
    lunes_proxima_semana = domingo_actual + timedelta(days=1)
    dias_proxima_semana = [lunes_proxima_semana + timedelta(days=i) for i in range(7)]

    return render_template(
        'index.html',
        dias_semana_actual=[(dia, dia.strftime('%A')) for dia in dias_semana_actual],
        dias_proxima_semana=[(dia, dia.strftime('%A')) for dia in dias_proxima_semana],
        turnos=turnos,
        dias_traducidos=dias_traducidos,
        hoy=hoy,
        turnos_faltantes=turnos_faltantes  # Pasar los turnos faltantes al template
    )

@main.route('/ping')
def ping():
    return "pong", 200
