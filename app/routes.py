import locale
from flask import Blueprint, render_template, request, redirect, url_for, Flask, Response, flash
from datetime import datetime, timedelta, date
import calendar
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

    # Calcular los próximos 3 días para los turnos faltantes
    proximos_3_dias = [hoy + timedelta(days=i) for i in range(3)]

    # Obtener los turnos faltantes para los próximos 3 días
    turnos_faltantes = []
    for dia in proximos_3_dias:
        for turno in ['día', 'noche']:
            if (dia, turno) not in turnos:
                turnos_faltantes.append({
                    'fecha': dia.strftime('%d/%m/%Y'),
                    'tipo': turno,
                    'dia': dias_traducidos[dia.strftime('%A')]
                })

    # Obtener el primer día del mes actual
    primer_dia_mes = date(hoy.year, hoy.month, 1)
    
    # Obtener el último día del mes actual
    if hoy.month == 12:
        ultimo_dia_mes = date(hoy.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia_mes = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    
    # Ajustar el primer_dia_mes al lunes de la semana si no es lunes
    dia_semana_primer_dia = primer_dia_mes.weekday()  # 0 = Lunes, 6 = Domingo
    if dia_semana_primer_dia > 0:  # Si no es lunes
        primer_dia_mes = primer_dia_mes - timedelta(days=dia_semana_primer_dia)
    
    # Ajustar ultimo_dia_mes al domingo de la semana si no es domingo
    dia_semana_ultimo_dia = ultimo_dia_mes.weekday()
    if dia_semana_ultimo_dia < 6:  # Si no es domingo
        ultimo_dia_mes = ultimo_dia_mes + timedelta(days=(6 - dia_semana_ultimo_dia))
    
    # Generar todas las semanas del mes (filtrando semanas pasadas)
    semanas = []
    fecha_actual = primer_dia_mes
    
    while fecha_actual <= ultimo_dia_mes:
        # Inicio de la semana (lunes)
        inicio_semana = fecha_actual
        
        # Fin de la semana (domingo)
        fin_semana = inicio_semana + timedelta(days=6)
        
        # Solo incluir la semana si el fin de la semana no es anterior a hoy
        # (es decir, si al menos un día de la semana es hoy o está en el futuro)
        if fin_semana >= hoy:
            # Días de esta semana
            dias_semana = []
            for i in range(7):  # lunes a domingo
                dia_actual = inicio_semana + timedelta(days=i)
                dias_semana.append((dia_actual, dia_actual.strftime('%A')))
            
            # Agregar la semana con el formato "Semana del 9 al 15 de Mayo"
            mes_inicio = inicio_semana.strftime('%B').capitalize()
            mes_fin = fin_semana.strftime('%B').capitalize()
            
            # Traducir los nombres de los meses al español
            meses_traducidos = {
                'January': 'Enero',
                'February': 'Febrero',
                'March': 'Marzo',
                'April': 'Abril',
                'May': 'Mayo',
                'June': 'Junio',
                'July': 'Julio',
                'August': 'Agosto',
                'September': 'Septiembre',
                'October': 'Octubre',
                'November': 'Noviembre',
                'December': 'Diciembre'
            }
            
            mes_inicio = meses_traducidos.get(mes_inicio, mes_inicio)
            mes_fin = meses_traducidos.get(mes_fin, mes_fin)
            
            # Formatear el título de la semana
            if mes_inicio == mes_fin:
                titulo_semana = f"Semana del {inicio_semana.day} al {fin_semana.day} de {mes_inicio}"
            else:
                titulo_semana = f"Semana del {inicio_semana.day} de {mes_inicio} al {fin_semana.day} de {mes_fin}"
            
            semanas.append({
                'titulo': titulo_semana,
                'dias': dias_semana,
                'es_semana_actual': hoy >= inicio_semana and hoy <= fin_semana
            })
        
        # Avanzar a la próxima semana
        fecha_actual = fin_semana + timedelta(days=1)

    return render_template(
        'index.html',
        semanas=semanas,
        turnos=turnos,
        dias_traducidos=dias_traducidos,
        hoy=hoy,
        turnos_faltantes=turnos_faltantes
    )

@main.route('/ping')
def ping():
    return "pong", 200
