import os
import datetime
from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- DISEÑO EJECUTIVO (MODERNO E INTERACTIVO) ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 40px 20px; }
    .container { max-width: 1000px; margin: auto; }
    
    .header { margin-bottom: 40px; border-left: 5px solid #0063ad; padding-left: 20px; }
    .header h1 { margin: 0; font-size: 26px; color: #0f172a; letter-spacing: -0.5px; }
    .header p { color: #64748b; margin: 5px 0 0 0; font-size: 14px; }

    .fecha-divider { margin: 30px 0 15px 0; font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; }
    .fecha-divider::after { content: ""; flex: 1; height: 1px; background: #e2e8f0; margin-left: 15px; }

    /* Estilo de la Lista */
    .registro-item { background: white; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 10px; overflow: hidden; transition: all 0.2s ease; cursor: pointer; }
    .registro-item:hover { border-color: #0063ad; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    
    /* Cabecera del Registro (Lo que siempre se ve) */
    .registro-header { padding: 18px 25px; display: flex; align-items: center; justify-content: space-between; }
    .user-info { display: flex; align-items: center; gap: 15px; }
    .user-initials { width: 40px; height: 40px; background: #e0f2fe; color: #0369a1; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
    .user-text b { display: block; font-size: 15px; color: #1e293b; }
    .user-text span { font-size: 12px; color: #64748b; }
    
    .actividad-tag { background: #f1f5f9; padding: 4px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; color: #475569; }
    .hora-tag { font-size: 12px; color: #94a3b8; font-weight: 500; }

    /* Contenido Expandible (Detalles ocultos) */
    .registro-details { max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; background: #fcfdfe; }
    .registro-item.active .registro-details { max-height: 800px; border-top: 1px solid #f1f5f9; }
    
    .details-inner { padding: 25px; display: grid; grid-template-columns: 280px 1fr; gap: 30px; }
    .photo-frame { width: 100%; border-radius: 12px; overflow: hidden; border: 4px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .photo-frame img { width: 100%; height: auto; display: block; }
    
    .data-sheet h3 { margin-top: 0; font-size: 14px; color: #0063ad; text-transform: uppercase; letter-spacing: 0.5px; }
    .data-sheet p { font-size: 15px; line-height: 1.6; color: #334155; white-space: pre-line; }

    @media (max-width: 768px) {
        .details-inner { grid-template-columns: 1fr; }
        .registro-header { flex-direction: column; align-items: flex-start; gap: 10px; }
        .hora-tag { order: -1; }
    }
</style>
"""

@app.route('/')
def visor_ejecutivo():
    try:
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client['NestleDB']
        puntos_col = db['Adminidtrativo']
        
        registros = list(puntos_col.find().sort("fecha", -1))

        # Agrupar por día para los separadores
        agrupado = {}
        for r in registros:
            f = r.get('fecha', '2026-01-01 00:00:00')
            dia = f.split(' ')[0]
            if dia not in agrupado: agrupado[dia] = []
            agrupado[dia].append(r)

        html = f"""
        <html>
        <head>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            {CSS}
        </head>
        <body>
            <div class='container'>
                <div class='header'>
                    <h1>Consola de Gestión Administrativa</h1>
                    <p>Monitoreo de actividades y validación de presencia - Nestlé</p>
                </div>
        """

        for dia, items in agrupado.items():
            html += f"<div class='fecha-divider'>{dia}</div>"
            
            for i, r in enumerate(items):
                nombre = r.get('nombre', 'Colaborador')
                iniciales = "".join([n[0] for n in nombre.split()[:2]])
                hora = r.get('fecha', '').split(' ')[1] if ' ' in r.get('fecha','') else '--:--'
                foto = r.get('foto', '')
                
                html += f"""
                <div class='registro-item' onclick='this.classList.toggle("active")'>
                    <div class='registro-header'>
                        <div class='user-info'>
                            <div class='user-initials'>{iniciales}</div>
                            <div class='user-text'>
                                <b>{nombre}</b>
                                <span>CC: {r.get('cedula','---')}</span>
                            </div>
                        </div>
                        <div class='actividad-tag'>{r.get('actividad','Sin actividad')}</div>
                        <div class='hora-tag'>{hora}</div>
                    </div>
                    <div class='registro-details'>
                        <div class='details-inner'>
                            <div class='photo-frame'>
                                <img src='{foto if foto else "https://via.placeholder.com/300x400?text=Sin+Foto"}'>
                            </div>
                            <div class='data-sheet'>
                                <h3>Resumen de Actividad</h3>
                                <p>{r.get('resumen','No se proporcionaron detalles adicionales.')}</p>
                                <hr style='border:0; border-top:1px solid #e2e8f0; margin:20px 0;'>
                                <div style='font-size:12px; color:#94a3b8;'>
                                    Validación de identidad vía Selfie realizada correctamente.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
        
        html += "</div></body></html>"
        return render_template_string(html)

    except Exception as e:
        return f"<div style='padding:40px; color:red; font-family:sans-serif;'><b>Error Crítico:</b> {str(e)}</div>"

if __name__ == "__main__":
    app.run()
    
