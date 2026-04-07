import os
import datetime
from flask import Flask, render_template_string
from pymongo import MongoClient

app = Flask(__name__)

# --- DISEÑO EJECUTIVO PREMIUM ---
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

    .registro-item { background: white; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 10px; overflow: hidden; transition: all 0.2s ease; cursor: pointer; }
    .registro-item:hover { border-color: #0063ad; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    
    .registro-header { padding: 18px 25px; display: flex; align-items: center; justify-content: space-between; }
    .user-info { display: flex; align-items: center; gap: 15px; }
    .user-initials { width: 40px; height: 40px; background: #e0f2fe; color: #0369a1; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
    .user-text b { display: block; font-size: 15px; color: #1e293b; }
    .user-text span { font-size: 12px; color: #64748b; }
    
    .actividad-tag { background: #f1f5f9; padding: 4px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; color: #475569; }
    .hora-tag { font-size: 12px; color: #94a3b8; font-weight: 500; }

    .registro-details { max-height: 0; overflow: hidden; transition: max-height 0.4s ease-out; background: #fcfdfe; }
    .registro-item.active .registro-details { max-height: 1000px; border-top: 1px solid #f1f5f9; }
    
    .details-inner { padding: 25px; display: grid; grid-template-columns: 280px 1fr; gap: 30px; }
    .photo-frame { width: 100%; border-radius: 12px; overflow: hidden; border: 4px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .photo-frame img { width: 100%; height: auto; display: block; background: #f1f5f9; }
    
    .data-sheet h3 { margin-top: 0; font-size: 14px; color: #0063ad; text-transform: uppercase; letter-spacing: 0.5px; }
    .data-sheet p { font-size: 15px; line-height: 1.6; color: #334155; white-space: pre-line; margin-bottom: 20px; }

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
        # Configuración de conexión (Asegúrate de tener MONGO_URI en Render)
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client['NestleDB']
        puntos_col = db['Adminidtrativo']
        
        # Obtenemos registros ordenados por fecha
        registros = list(puntos_col.find().sort("fecha", -1))

        if not registros:
            return "<html><body style='text-align:center; padding-top:100px; font-family:sans-serif;'><h2>Sin registros</h2><p>No se encontraron datos en la colección 'Adminidtrativo'.</p></body></html>"

        # Agrupación lógica por día
        agrupado = {}
        for r in registros:
            f_raw = r.get('fecha')
            
            # --- MANEJO DE ERROR DATETIME.SPLIT ---
            if isinstance(f_raw, datetime.datetime):
                f_str = f_raw.strftime("%Y-%m-%d %H:%M:%S")
            elif f_raw:
                f_str = str(f_raw)
            else:
                f_str = "2026-01-01 00:00:00"
            
            dia = f_str.split(' ')[0]
            if dia not in agrupado:
                agrupado[dia] = []
            
            r['fecha_formateada'] = f_str
            agrupado[dia].append(r)

        # Generación del HTML
        html = f"""
        <html>
        <head>
            <title>Panel Administrativo Nestlé</title>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            {CSS}
        </head>
        <body>
            <div class='container'>
                <div class='header'>
                    <h1>Consola de Gestión Administrativa</h1>
                    <p>Visor ejecutivo de reportes y validación de personal</p>
                </div>
        """

        for dia, items in agrupado.items():
            html += f"<div class='fecha-divider'>{dia}</div>"
            
            for r in items:
                nombre = r.get('nombre', 'Usuario Nestlé')
                # Iniciales dinámicas
                parts = nombre.split()
                ini = (parts[0][0] + parts[1][0]).upper() if len(parts) > 1 else parts[0][0].upper()
                
                # Hora extraída del string formateado
                f_text = r['fecha_formateada']
                hora = f_text.split(' ')[1] if ' ' in f_text else '--:--'
                
                foto = r.get('foto', '')

                html += f"""
                <div class='registro-item' onclick='this.classList.toggle("active")'>
                    <div class='registro-header'>
                        <div class='user-info'>
                            <div class='user-initials'>{ini}</div>
                            <div class='user-text'>
                                <b>{nombre}</b>
                                <span>CC: {r.get('cedula','---')}</span>
                            </div>
                        </div>
                        <div class='actividad-tag'>{r.get('actividad','General')}</div>
                        <div class='hora-tag'>{hora}</div>
                    </div>
                    <div class='registro-details'>
                        <div class='details-inner'>
                            <div class='photo-frame'>
                                <img src='{foto if foto else "https://via.placeholder.com/300x400?text=Sin+Selfie"}' loading='lazy'>
                            </div>
                            <div class='data-sheet'>
                                <h3>Detalle de la Jornada</h3>
                                <p>{r.get('resumen','Sin resumen detallado proporcionado.')}</p>
                                <hr style='border:0; border-top:1px solid #e2e8f0; margin:20px 0;'>
                                <div style='font-size:12px; color:#94a3b8; font-style: italic;'>
                                    Registro ingresado el {f_text}. Identidad validada mediante captura biométrica.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
        
        html += """
            </div>
            <script>
                // Script opcional para cerrar otros al abrir uno (estilo acordeón puro)
                // Actualmente permite abrir varios a la vez para comparar.
            </script>
        </body>
        </html>
        """
        return render_template_string(html)

    except Exception as e:
        return f"<div style='padding:50px; color:#e11d48; font-family:sans-serif; background:#fff1f2; border:1px solid #fda4af; border-radius:12px; max-width:600px; margin:auto; margin-top:50px;'><b>Error de Sistema:</b> {str(e)}</div>"

if __name__ == "__main__":
    app.run()
