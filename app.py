import os
import datetime
from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- CONEXIÓN MONGODB ---
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['NestleDB']
puntos_col = db['Adminidtrativo']

# --- DISEÑO UI PREMIUM ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    body { font-family: 'Poppins', sans-serif; background: #f4f7fa; margin: 0; padding: 20px; color: #333; }
    .header { text-align: center; padding: 20px 0; margin-bottom: 30px; border-bottom: 2px solid #0063ad; }
    .header h1 { color: #0063ad; margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 1px; }
    
    .fecha-section { margin-bottom: 50px; }
    .fecha-badge { background: #0063ad; color: white; padding: 8px 25px; border-radius: 30px; font-weight: 600; display: inline-block; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 25px; }
    
    .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.05); transition: 0.3s; display: flex; flex-direction: column; }
    .card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); }
    
    .img-container { width: 100%; height: 220px; background: #eee; position: relative; }
    .img-container img { width: 100%; height: 100%; object-fit: cover; }
    .overlay-name { position: absolute; bottom: 0; width: 100%; background: linear-gradient(transparent, rgba(0,0,0,0.8)); color: white; padding: 15px; box-sizing: border-box; }
    .overlay-name b { font-size: 1.1em; display: block; }
    .overlay-name span { font-size: 0.8em; opacity: 0.9; }

    .content { padding: 15px; flex-grow: 1; }
    .entry { border-left: 3px solid #00a1e1; padding-left: 12px; margin-bottom: 15px; }
    .entry-time { font-size: 11px; color: #999; font-weight: 600; }
    .entry-act { font-weight: 600; color: #0063ad; margin: 3px 0; display: block; }
    .entry-res { font-size: 13px; color: #666; line-height: 1.4; }
    
    .empty { text-align: center; padding: 100px; color: #999; }
</style>
"""

@app.route('/')
def visor_principal():
    # Obtener registros ordenados por fecha descendente
    registros = list(puntos_col.find().sort([("fecha", -1), ("nombre", 1)]))
    
    if not registros:
        return render_template_string(f"<html><head>{CSS}</head><body><div class='empty'>No hay registros en la base de datos.</div></body></html>")

    # Agrupación por Fecha -> Cédula
    data_agrupada = {}
    for r in registros:
        # Extraer fecha y hora
        f_raw = r.get('fecha', '2026-01-01 00:00:00')
        dia = f_raw.split(' ')[0]
        hora = f_raw.split(' ')[1] if ' ' in f_raw else "00:00"
        
        if dia not in data_agrupada: data_agrupada[dia] = {}
        
        ced = r.get('cedula', '000')
        if ced not in data_agrupada[dia]:
            data_agrupada[dia][ced] = {
                "nombre": r.get('nombre', 'Usuario Desconocido'),
                "foto": r.get('foto'),
                "registros": []
            }
        
        data_agrupada[dia][ced]["registros"].append({
            "hora": hora,
            "actividad": r.get('actividad', 'N/A'),
            "resumen": r.get('resumen', 'N/A')
        })

    # Construcción HTML
    html = f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{CSS}</head><body>"
    html += "<div class='header'><h1>📊 Visor de Base de Datos - Nestlé</h1></div>"

    for dia, personas in data_agrupada.items():
        html += f"<div class='fecha-section'><div class='fecha-badge'>📅 {dia}</div>"
        html += "<div class='grid'>"
        
        for ced, info in personas.items():
            foto_src = info['foto'] if info['foto'] else "https://via.placeholder.com/400x300?text=Sin+Foto"
            html += f"""
            <div class='card'>
                <div class='img-container'>
                    <img src='{foto_src}' loading='lazy'>
                    <div class='overlay-name'>
                        <b>{info['nombre']}</b>
                        <span>Cédula: {ced}</span>
                    </div>
                </div>
                <div class='content'>
            """
            for reg in info['registros']:
                html += f"""
                    <div class='entry'>
                        <span class='entry-time'>🕒 {reg['hora']}</span>
                        <span class='entry-act'>{reg['actividad']}</span>
                        <span class='entry-res'>{reg['resumen']}</span>
                    </div>
                """
            html += "</div></div>"
        
        html += "</div></div>"
    
    html += "</body></html>"
    return render_template_string(html)

if __name__ == "__main__":
    # Render usa gunicorn, pero para pruebas locales:
    app.run(host='0.0.0.0', port=5000)
