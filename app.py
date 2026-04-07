import os
import datetime
from flask import Flask, render_template_string, request
from pymongo import MongoClient

app = Flask(__name__)

# --- DISEÑO EJECUTIVO OPTIMIZADO ---
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    body { font-family: 'Inter', sans-serif; background: #f1f5f9; color: #1e293b; margin: 0; padding: 20px; }
    .container { max-width: 900px; margin: auto; }
    
    /* Filtro de Fecha */
    .filter-bar { background: white; padding: 20px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px; }
    .filter-bar input { padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-family: inherit; }
    .filter-bar button { background: #0063ad; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
    .filter-bar a { font-size: 13px; color: #64748b; text-decoration: none; }

    .header-main { margin-bottom: 25px; }
    .header-main h1 { font-size: 22px; color: #0f172a; margin: 0; }

    .fecha-label { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin: 20px 0 10px 10px; display: block; }

    /* Tarjeta Agrupada */
    .card-resumen { background: white; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 15px; overflow: hidden; cursor: pointer; transition: 0.2s; }
    .card-resumen:hover { border-color: #0063ad; }
    
    .card-visible { padding: 20px; display: flex; align-items: center; justify-content: space-between; }
    .user-profile { display: flex; align-items: center; gap: 15px; }
    .avatar { width: 45px; height: 45px; background: #0063ad; color: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 700; }
    .user-data b { display: block; font-size: 15px; }
    .user-data span { font-size: 12px; color: #64748b; }
    
    .badge-conteo { background: #e0f2fe; color: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }

    /* Detalles Expandidos */
    .card-hidden { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; background: #fafcfe; }
    .card-resumen.active .card-hidden { max-height: 1200px; border-top: 1px solid #f1f5f9; }
    
    .detail-grid { padding: 25px; display: grid; grid-template-columns: 250px 1fr; gap: 25px; }
    .photo-side img { width: 100%; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    .activities-list { margin: 0; padding: 0; list-style: none; }
    .activity-item { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #edf2f7; }
    .activity-item:last-child { border: none; }
    .act-title { font-weight: 700; color: #0063ad; font-size: 14px; display: block; margin-bottom: 4px; }
    .act-desc { font-size: 13.5px; color: #475569; line-height: 1.5; }

    @media (max-width: 700px) { .detail-grid { grid-template-columns: 1fr; } }
</style>
"""

@app.route('/')
def visor_optimizado():
    try:
        # Conexión
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://ANDRES_VANEGAS:CF32fUhOhrj70dY5@cluster0.dtureen.mongodb.net/?appName=Cluster0")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client['NestleDB']
        puntos_col = db['Adminidtrativo']

        # Filtro de fecha
        fecha_busqueda = request.args.get('fecha_filtro', '')
        query = {}
        if fecha_busqueda:
            # Busca registros que comiencen con la fecha elegida (YYYY-MM-DD)
            query = {"fecha": {"$regex": f"^{fecha_busqueda}"}}

        registros = list(puntos_col.find(query).sort("fecha", -1))

        # AGRUPACIÓN MAESTRA: Día -> Persona
        # Estructura: { "2026-04-06": { "123": {"nombre": "Ana", "foto": "...", "notas": [...]} } }
        agrupado = {}
        for r in registros:
            f_raw = r.get('fecha')
            f_str = f_raw.strftime("%Y-%m-%d %H:%M:%S") if isinstance(f_raw, datetime.datetime) else str(f_raw)
            dia = f_str.split(' ')[0]
            ced = r.get('cedula', 'S/C')

            if dia not in agrupado: agrupado[dia] = {}
            if ced not in agrupado[dia]:
                agrupado[dia][ced] = {
                    "nombre": r.get('nombre', 'Usuario'),
                    "foto": r.get('foto'),
                    "notas": []
                }
            
            agrupado[dia][ced]["notas"].append({
                "act": r.get('actividad', 'N/A'),
                "res": r.get('resumen', 'N/A')
            })

        html = f"""
        <html>
        <head>
            <meta name='viewport' content='width=device-width, initial-scale=1'>
            {CSS}
        </head>
        <body>
            <div class='container'>
                <div class='header-main'>
                    <h1>Panel de Control Nestlé</h1>
                </div>

                <form class='filter-bar' method='GET'>
                    <input type='date' name='fecha_filtro' value='{fecha_busqueda}'>
                    <button type='submit'>Filtrar</button>
                    <a href='/'>Limpiar</a>
                </form>
        """

        if not agrupado:
            html += "<div style='text-align:center; padding:50px; color:#94a3b8;'>No hay registros para este criterio.</div>"

        for dia, personas in agrupado.items():
            html += f"<span class='fecha-label'>{dia}</span>"
            for ced, data in personas.items():
                iniciales = "".join([n[0] for n in data['nombre'].split()[:2]]).upper()
                conteo = len(data['notas'])
                
                html += f"""
                <div class='card-resumen' onclick='this.classList.toggle("active")'>
                    <div class='card-visible'>
                        <div class='user-profile'>
                            <div class='avatar'>{iniciales}</div>
                            <div class='user-data'>
                                <b>{data['nombre']}</b>
                                <span>CC: {ced}</span>
                            </div>
                        </div>
                        <div class='badge-conteo'>{conteo} actividades registradas</div>
                    </div>
                    <div class='card-hidden'>
                        <div class='detail-grid'>
                            <div class='photo-side'>
                                <img src='{data['foto'] if data['foto'] else "https://via.placeholder.com/300x400?text=Sin+Foto"}' loading='lazy'>
                            </div>
                            <div class='activities-side'>
                                <ul class='activities-list'>
                """
                for n in data['notas']:
                    html += f"""
                                    <li class='activity-item'>
                                        <span class='act-title'>{n['act']}</span>
                                        <span class='act-desc'>{n['res']}</span>
                                    </li>
                    """
                html += """
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                """

        html += "</div></body></html>"
        return render_template_string(html)

    except Exception as e:
        return f"<div style='padding:30px; background:#fee2e2; color:#b91c1c; border-radius:10px;'><b>Error de sistema:</b> {str(e)}</div>"

if __name__ == "__main__":
    app.run()
