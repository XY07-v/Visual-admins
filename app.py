import os
import datetime
import base64
from flask import Flask, request, render_template_string, session, redirect, url_for
from flask_session import Session
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURACIÓN DE SESIÓN ---
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=8)
app.config["SECRET_KEY"] = "Nestle_Full_Access_2026"
Session(app)

# --- CONEXIÓN MONGODB ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['NestleDB']
puntos_col = db['Adminidtrativo']

# --- DICCIONARIO DE USUARIOS (30 COLABORADORES) ---
usuarios = {
    "1094938475": "AMADO LOZANO JHEINER ALBEIRO", "1042064101": "ARDILA ORTEGA FABIANA",
    "1020811447": "BAQUERO MURCIA CRISTIAN CAMILO", "1143360426": "BARRERA DE AVILA KELLY JOHANA",
    "1121833139": "BOCANEGRA GARZON CINDY JULIETH", "1053783753": "CARMONA HUERTAS NESTOR ANDRES",
    "52860228": "CASTRILLON URREGO YEIMI PAOLA", "1048276830": "CASTRO OROZCO CINDY PAOLA",
    "1085248529": "ERAZO CAICEDO DIANA MARCELA", "1023930172": "FORERO VELASQUEZ EDWIN ALEXANDER",
    "1143341974": "GONZALES BERRIO YEISON JOSE", "1022404439": "GONZALEZ RODRIGUEZ MICHAEL",
    "1095835233": "GRIMALDO NAVARRO WILSON JAVIER", "1015068243": "HINCAPIE ZEA YOANA ANDREA",
    "1053334868": "JIMENEZ JIMENEZ ESNEYDI YELEYSI", "1010070556": "KAREN TATIANA DE LA ROSA TORRES",
    "1003634117": "MARIN GALEANO KEVIN SANTIAGO", "1037948290": "MAURICIO LADINO LARGO",
    "1072703990": "MERCHAN SEGURA JOHN EDISON", "1234990099": "MONTOYA BUITRAGO VANESA",
    "1018438044": "ORJUELA FORIGUA HAYDE CAROLINA", "43268846": "OTALVARO METAUTE MONICA MILENA",
    "1002183801": "PADILLA GRAVIER JUAN CAMILO", "43753705": "PATIÑO MONICA MARIA",
    "1113661456": "RAMIREZ MORENO GERALDINE", "80220107": "RAMIREZ SARAY SIGIFREDO",
    "66771000": "RESTREPO LUZ MARLENE", "93236326": "SIERRA PELAEZ RIGOBERTO",
    "43161032": "YEPES BETANCUR SHIRLEY", "1130589169": "ELIECER ARDILA LUCIO"
}

# --- ESTILOS CSS ---
CSS = """
<style>
    :root { --nestle-blue: #0063ad; --bg: #f0f2f5; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); margin: 0; padding: 20px; }
    .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; margin: auto; text-align: center; }
    input, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
    button { background: var(--nestle-blue); color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; margin-top: 20px; }
    th { background: var(--nestle-blue); color: white; padding: 12px; text-align: left; font-size: 0.9em; }
    td { padding: 10px; border-bottom: 1px solid #eee; font-size: 0.85em; }
    .img-cell img { width: 60px; border-radius: 4px; cursor: zoom-in; transition: 0.3s; }
    .img-cell img:hover { transform: scale(3); position: relative; z-index: 10; }
    .nav-links { text-align: center; margin-bottom: 20px; }
    .nav-links a { margin: 0 10px; text-decoration: none; color: var(--nestle-blue); font-weight: bold; }
</style>
"""

# --- RUTAS DE REGISTRO (TRABAJADORES) ---

@app.route('/')
def index():
    if "user" in session: return redirect(url_for('registro'))
    content = """
    <div class='card'>
        <h2 style='color: #0063ad'>Registro Nestlé</h2>
        <form action="/login" method="post">
            <input type="text" name="cedula" placeholder="Cédula" required>
            <button type="submit">Entrar</button>
        </form>
        <br><a href="/visor_total" style="font-size: 0.8em; color: gray;">Ver Base de Datos (Visor)</a>
    </div>
    """
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>{content}</body></html>")

@app.route('/login', methods=['POST'])
def login():
    ced = request.form.get('cedula')
    if ced in usuarios:
        session["user"], session["nombre"] = ced, usuarios[ced]
        return redirect(url_for('foto'))
    return "Cédula no válida. <a href='/'>Volver</a>"

@app.route('/foto')
def foto():
    if "user" not in session: return redirect(url_for('index'))
    if "foto_ok" in session: return redirect(url_for('registro'))
    content = f"""
    <div class='card'>
        <h3>Paso 1: Selfie Obligatoria</h3>
        <p>{session['nombre']}</p>
        <p style='color: orange; font-size: 0.9em;'>📷 Uniforme claro y frente al PC</p>
        <form action="/subir_foto" method="post" enctype="multipart/form-data">
            <input type="file" name="foto" accept="image/*" capture="user" required>
            <button type="submit">Subir y Continuar</button>
        </form>
    </div>
    """
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>{content}</body></html>")

@app.route('/subir_foto', methods=['POST'])
def subir_foto():
    file = request.files['foto']
    if file:
        img_b64 = base64.b64encode(file.read()).decode('utf-8')
        session["foto_ok"] = f"data:image/jpeg;base64,{img_b64}"
    return redirect(url_for('registro'))

@app.route('/registro')
def registro():
    if "foto_ok" not in session: return redirect(url_for('foto'))
    content = f"""
    <div class='card'>
        <h4>Nueva Nota de Trabajo</h4>
        <form action="/guardar" method="post">
            <input type="text" name="actividad" placeholder="Actividad" required>
            <textarea name="resumen" placeholder="Resumen detallado..." rows="4" required></textarea>
            <button type="submit">Guardar Registro</button>
        </form>
        <br><a href="/logout" style="color:red; font-size:0.8em;">Cerrar Sesión</a>
    </div>
    """
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>{content}</body></html>")

@app.route('/guardar', methods=['POST'])
def guardar():
    if "user" not in session: return redirect(url_for('index'))
    puntos_col.insert_one({
        "cedula": session["user"],
        "nombre": session["nombre"],
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actividad": request.form.get('actividad'),
        "resumen": request.form.get('resumen'),
        "foto": session.get("foto_ok")
    })
    return redirect(url_for('registro'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- MÓDULO VISOR TOTAL (SIN LOGUEO - TODA LA BD) ---

@app.route('/visor_total')
def visor_total():
    # Consultamos TODOS los registros sin filtros, del más reciente al más antiguo
    registros = list(puntos_col.find().sort("_id", -1))
    
    tabla_html = """
    <div class="nav-links"><a href="/">Ir al Registro</a> | <b>Visor de Base de Datos Total</b></div>
    <table>
        <tr>
            <th>Fecha</th>
            <th>Cédula</th>
            <th>Nombre</th>
            <th>Actividad</th>
            <th>Resumen</th>
            <th>Foto</th>
        </tr>
    """
    for r in registros:
        img_tag = f"<div class='img-cell'><img src='{r.get('foto')}'></div>" if r.get('foto') else "N/A"
        tabla_html += f"""
        <tr>
            <td>{r.get('fecha')}</td>
            <td>{r.get('cedula')}</td>
            <td>{r.get('nombre')}</td>
            <td>{r.get('actividad')}</td>
            <td>{r.get('resumen')}</td>
            {img_tag}
        </tr>
        """
    tabla_html += "</table>"
    
    return render_template_string(f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>{tabla_html}</body></html>")

if __name__ == "__main__":
    app.run()
