import os
import datetime
from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURACIÓN DE ESTILOS ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    body { font-family: 'Poppins', sans-serif; background: #f0f4f8; margin: 0; padding: 20px; color: #1a202c; }
    .header { text-align: center; padding: 30px 0; border-bottom: 3px solid #0063ad; margin-bottom: 40px; background: white; border-radius: 0 0 20px 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .header h1 { color: #0063ad; margin: 0; font-size: 28px; letter-spacing: 1px; }
    
    .fecha-badge { background: #0063ad; color: white; padding: 10px 25px; border-radius: 50px; font-weight: 600; display: inline-block; margin: 20px 0; box-shadow: 0 4px 10px rgba(0,99,173,0.2); }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 30px; }
    
    .card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); transition: transform 0.3s ease; display: flex; flex-direction: column; }
    .card:hover { transform: translateY(-10px); }
    
    .img-box { width: 100%; height: 250px; background: #e2e8f0; position: relative; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; }
    .name-tag { position: absolute; bottom: 0; width: 100%; background: linear-gradient(transparent, rgba(0,0,0,0.9)); color: white; padding: 20px 15px 10px 15px; box-sizing: border-box; }
    .name-tag b { font-size: 1.2em; display: block; }
    .name-tag span { font-size: 0.85em; opacity: 0.8; }

    .notes { padding: 20px; flex-grow: 1; }
    .note-row { border-left: 4px solid #00a1e1; padding-left: 15px; margin-bottom: 20px; position: relative; }
    .note-time { font-size: 0.75em; color: #a0aec0; font-weight: 600; text-transform: uppercase; }
    .note-act { font-weight: 600; color: #2d3748; margin: 5px 0; display: block; font-size: 1.05em; }
    .note-res { font-size: 14px; color: #4a5568; line-height: 1.5; font-style: italic; }
    
    .error-box { background: #fff5f5; color: #c53030; padding: 20px; border-radius: 10px; border: 1px solid #feb2b2; max-width: 600px; margin: 50px auto; }
</style>
"""

@app.route('/')
def visor_total():
    try:
        # Intentar conectar a MongoDB
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client['NestleDB']
        puntos_col = db['Adminidtrativo']
        
        # Obtener todos los registros (orden: fecha más reciente primero)
        registros = list(puntos_col.find().sort([("fecha", -1), ("nombre", 1)]))
        
        if not registros:
            return render_template_string(f"<html><head>{CSS}</head><body><div style='text-align:center; padding:100px;'><h3>Base de datos vacía</h3><p>No se encontraron registros en 'Adminidtrativo'.</p></div></body></html>")

        # Agrupar por Día -> Cédula
        data_final = {}
        for r in registros:
            f_full = r.get('fecha', '2026-01-01 00:00:00')
            # Manejar si la fecha ya es un string o un objeto datetime
            str_fecha = f_full if isinstance(f_full, str) else f_full.strftime("%Y-%m-%d %H:%M:%S")
            dia = str_fecha.split(' ')[0]
            hora = str_fecha.split(' ')[1] if ' ' in str_fecha else "00:00"
            
            if dia not in data_final: data_final[dia] = {}
            
            ced = r.get('cedula', 'S/N')
            if ced not in data_final[dia]:
                data_final[dia][ced] = {
                    "nombre": r.get('nombre', 'Desconocido'),
                    "foto": r.get('foto'),
                    "items": []
                }
            
            data_final[dia][ced]["items"].append({
                "hora": hora,
                "actividad": r.get('actividad', 'Sin actividad'),
                "resumen": r.get('resumen', 'Sin resumen')
            })

        # Construir la interfaz
        html = f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>"
        html += "<div class='header'><h1>REPORTES ADMINISTRATIVOS NESTLÉ</h1></div>"

        for dia, personas in data_final.items():
            html += f"<div class='fecha-badge'>📅 {dia}</div>"
            html += "<div class='grid'>"
            
            for ced, info in personas.items():
                foto_url = info['foto'] if info['foto'] else "https://via.placeholder.com/400x300?text=Sin+Selfie"
                html += f"""
                <div class='card'>
                    <div class='img-box'>
                        <img src='{foto_url}' loading='lazy'>
                        <div class='name-tag'>
                            <b>{info['nombre']}</b>
                            <span>CC: {ced}</span>
                        </div>
                    </div>
                    <div class='notes'>
                """
                for item in info['items']:
                    html += f"""
                        <div class='note-row'>
                            <span class='note-time'>🕒 {item['hora']}</span>
                            <span class='note-act'>{item['actividad']}</span>
                            <span class='note-res'>"{item['resumen']}"</span>
                        </div>
                    """
                html += "</div></div>"
            html += "</div>"
        
        html += "</body></html>"
        return render_template_string(html)

    except Exception as e:
        # Esto atrapará el error 500 y te dirá qué pasó (IP bloqueada, mala URI, etc.)
        return render_template_string(f"""
        <html><head>{CSS}</head><body>
            <div class='error-box'>
                <h2>❌ Error de Conexión</h2>
                <p>No se pudo conectar a MongoDB. Revisa lo siguiente:</p>
                <ul>
                    <li>Que tu IP esté autorizada en MongoDB Atlas (Network Access -> 0.0.0.0/0).</li>
                    <li>Que la contraseña en la URI sea correcta.</li>
                </ul>
                <hr>
                <small>Detalle técnico: {str(e)}</small>
            </div>
        </body></html>
        """)

if __name__ == "__main__":
    app.run()
