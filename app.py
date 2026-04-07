import os
import datetime
import base64
from flask import Flask, request, render_template_string, session, redirect, url_for
from flask_session import Session
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURACIÓN DE SESIÓN (8 HORAS) ---
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=8)
app.config["SECRET_KEY"] = "Nestle_Secret_2024"
Session(app)

# --- CONEXIÓN MONGODB ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['NestleDB']
puntos_col = db['Adminidtrativo']

# --- DICCIONARIO DE USUARIOS ---
usuarios = {
    "1094938475": "AMADO LOZANO JHEINER ALBEIRO",
    "1042064101": "ARDILA ORTEGA FABIANA",
    "1020811447": "BAQUERO MURCIA CRISTIAN CAMILO",
    "1143360426": "BARRERA DE AVILA KELLY JOHANA",
    "1121833139": "BOCANEGRA GARZON CINDY JULIETH",
    "1053783753": "CARMONA HUERTAS NESTOR ANDRES",
    "52860228": "CASTRILLON URREGO YEIMI PAOLA",
    "1048276830": "CASTRO OROZCO CINDY PAOLA",
    "1085248529": "ERAZO CAICEDO DIANA MARCELA",
    "1023930172": "FORERO VELASQUEZ EDWIN ALEXANDER",
    "1143341974": "GONZALES BERRIO YEISON JOSE",
    "1022404439": "GONZALEZ RODRIGUEZ MICHAEL",
    "1095835233": "GRIMALDO NAVARRO WILSON JAVIER",
    "1015068243": "HINCAPIE ZEA YOANA ANDREA",
    "1053334868": "JIMENEZ JIMENEZ ESNEYDI YELEYSI",
    "1010070556": "KAREN TATIANA DE LA ROSA TORRES",
    "1003634117": "MARIN GALEANO KEVIN SANTIAGO",
    "1037948290": "MAURICIO LADINO LARGO",
    "1072703990": "MERCHAN SEGURA JOHN EDISON",
    "1234990099": "MONTOYA BUITRAGO VANESA",
    "1018438044": "ORJUELA FORIGUA HAYDE CAROLINA",
    "43268846": "OTALVARO METAUTE MONICA MILENA",
    "1002183801": "PADILLA GRAVIER JUAN CAMILO",
    "43753705": "PATIÑO MONICA MARIA",
    "1113661456": "RAMIREZ MORENO GERALDINE",
    "80220107": "RAMIREZ SARAY SIGIFREDO",
    "66771000": "RESTREPO LUZ MARLENE",
    "93236326": "SIERRA PELAEZ RIGOBERTO",
    "43161032": "YEPES BETANCUR SHIRLEY",
    "1130589169": "ELIECER ARDILA LUCIO"
}

# --- DISEÑO UI ---
CSS = """
<style>
    :root { --primary: #0063ad; --secondary: #00a1e1; --bg: #f8f9fa; }
    body { font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.1); width: 90%; max-width: 450px; text-align: center; }
    input, textarea { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; font-size: 16px; }
    button { background: var(--primary); color: white; border: none; padding: 14px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 10px; }
    .instr { background: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; font-size: 0.9em; margin-bottom: 15px; border: 1px solid #ffeeba; text-align: left; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.8em; }
    th { background: var(--primary); color: white; padding: 10px; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .thumb { width: 80px; border-radius: 5px; cursor: pointer; }
</style>
"""

LAYOUT = f"<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body><div class='card'>{{{{ content | safe }}}}</div></body></html>"

# --- RUTAS DE REGISTRO ---

@app.route('/')
def index():
    if "user" in session:
        return redirect(url_for('registro'))
    content = """
    <h2 style='color:#0063ad'>Nestlé Admin</h2>
    <form action="/login" method="post">
        <input type="text" name="cedula" placeholder="Número de Cédula" required>
        <button type="submit">Ingresar</button>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/login', methods=['POST'])
def login():
    ced = request.form.get('cedula')
    if ced in usuarios:
        session["user"] = ced
        session["nombre"] = usuarios[ced]
        return redirect(url_for('verificar_foto'))
    return "Cédula no registrada. <a href='/'>Volver</a>"

@app.route('/foto')
def verificar_foto():
    if "user" not in session: return redirect(url_for('index'))
    if "foto_b64" in session: return redirect(url_for('registro'))
    
    content = f"""
    <h3>Paso Obligatorio</h3>
    <p>{session['nombre']}</p>
    <div class='instr'>🤳 <b>SELFIE REQUERIDA:</b><br>Frente al PC, con uniforme visible y clara. Solo se pide una vez por sesión.</div>
    <form action="/subir_foto" method="post" enctype="multipart/form-data">
        <input type="file" name="foto" accept="image/*" capture="user" required>
        <button type="submit">Validar Foto e Iniciar</button>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/subir_foto', methods=['POST'])
def subir_foto():
    file = request.files['foto']
    if file:
        # Convertimos la imagen a Base64 para guardarla en MongoDB
        img_b64 = base64.b64encode(file.read()).decode('utf-8')
        session["foto_b64"] = f"data:image/jpeg;base64,{img_b64}"
    return redirect(url_for('registro'))

@app.route('/registro')
def registro():
    if "user" not in session: return redirect(url_for('index'))
    if "foto_b64" not in session: return redirect(url_for('verificar_foto'))
    
    content = f"""
    <h4>Registro de Actividad</h4>
    <p style='font-size:0.8em; color:gray'>{session['nombre']}</p>
    <form action="/guardar" method="post">
        <input type="text" name="actividad" placeholder="¿Qué estás haciendo?" required>
        <textarea name="resumen" placeholder="Resumen detallado..." rows="4" required></textarea>
        <button type="submit">Guardar Registro</button>
    </form>
    <hr>
    <a href="/logout" style="color:red; text-decoration:none; font-size:0.8em;">Cerrar Sesión</a>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/guardar', methods=['POST'])
def guardar():
    if "user" not in session: return redirect(url_for('index'))
    
    registro_data = {
        "cedula": session["user"],
        "nombre": session["nombre"],
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actividad": request.form.get('actividad'),
        "resumen": request.form.get('resumen'),
        "foto": session.get("foto_b64")
    }
    puntos_col.insert_one(registro_data)
    return render_template_string(LAYOUT, content="<h3>✅ Guardado</h3><p>Registro almacenado correctamente.</p><a href='/registro'><button>Nueva Nota</button></a>")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- RUTA DEL DASHBOARD (ADMIN) ---

@app.route('/admin/panel')
def admin_panel():
    # Buscamos los últimos registros
    datos = list(puntos_col.find().sort("_id", -1).limit(100))
    
    tabla_html = """
    <h2 style='max-width:900px; margin:auto'>Panel de Control</h2>
    <div style='max-width:1000px; margin:auto; overflow-x:auto; background:white; padding:15px; border-radius:10px;'>
    <table>
        <tr>
            <th>Fecha</th>
            <th>Nombre</th>
            <th>Actividad</th>
            <th>Resumen</th>
            <th>Foto</th>
        </tr>
    """
    for r in datos:
        foto_td = f"<td><img src='{r.get('foto')}' class='thumb'></td>" if r.get('foto') else "<td>Sin foto</td>"
        tabla_html += f"""
        <tr>
            <td>{r.get('fecha')}</td>
            <td>{r.get('nombre')}</td>
            <td>{r.get('actividad')}</td>
            <td>{r.get('resumen')}</td>
            {foto_td}
        </tr>
        """
    tabla_html += "</table></div><br><center><a href='/'>Ir al Login</a></center>"
    
    # Usamos un layout más ancho para el admin
    ADMIN_LAYOUT = f"<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body style='display:block; padding:20px;'>{tabla_html}</body></html>"
    return render_template_string(ADMIN_LAYOUT)

if __name__ == "__main__":
    app.run()
