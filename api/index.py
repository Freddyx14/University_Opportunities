import sys
import os
import traceback

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

try:
    print("Intentando importar app...")
    # Intentamos cargar variables de entorno manualmente por si acaso
    from dotenv import load_dotenv
    load_dotenv(os.path.join(root_dir, '.env'))
    
    # Importamos paso a paso para ver dónde falla
    print("Importando flask...")
    from flask import Flask
    
    print("Importando app.py...")
    from app import app
    print("APP IMPORTADA CON ÉXITO")

except Exception as e:
    print(f"Error capturado: {e}")
    from flask import Flask
    app = Flask(__name__)
    
    error_msg = traceback.format_exc()
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all_error(path):
        return f"""
        <html>
            <body style="font-family: monospace; padding: 20px; background: #FFF0F0;">
                <h1 style="color: #D8000C;">Error Crítico de Importación</h1>
                <p>La aplicación no pudo iniciar. Aquí está el detalle:</p>
                <div style="background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                    <pre>{error_msg}</pre>
                </div>
                <h3>Estructura de Directorios:</h3>
                <pre>{str(os.listdir(root_dir))}</pre>
                <h3>Variables de Entorno Detectadas:</h3>
                <pre>{', '.join([k for k in os.environ.keys() if 'KEY' in k or 'URL' in k or 'SECRET' in k])}</pre>
            </body>
        </html>
        """
