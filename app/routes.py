import locale
from flask import Blueprint, render_template, request, redirect, url_for, Flask, Response
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
            except:
                db.session.rollback()
        elif action == 'cancelar':
            Turno.query.filter_by(fecha=fecha, tipo=tipo).delete()
            db.session.commit()

        return redirect(url_for('main.index'))


    locale.setlocale(locale.LC_TIME, 'C')

    hoy = datetime.today().date()
    mañana = hoy + timedelta(days=1)
    dias_raw = [hoy + timedelta(days=i) for i in range(7)]
    dias = [(dia, dia.strftime('%A')) for dia in dias_raw]

    dias_traducidos = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    turnos = {(t.fecha, t.tipo): t.nombre for t in Turno.query.all()}
    return render_template('index.html', dias=dias, turnos=turnos, dias_traducidos=dias_traducidos, hoy=hoy, mañana=mañana)
