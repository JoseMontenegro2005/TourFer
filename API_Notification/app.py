from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import threading

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Enviando vía Resend API a {destinatario}...", flush=True)
        
        # Configuración de la petición a Resend
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # NOTA: En el modo de prueba de Resend, solo puedes enviar correos 
        # a la dirección con la que te registraste.
        payload = {
            "from": "TourFer <onboarding@resend.dev>", # Correo genérico permitido por Resend
            "to": [destinatario],
            "subject": "Confirmación de Reserva - TourFer",
            "html": f"<p>{mensaje_texto}</p>" # Soporta HTML básico
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"✅ [Background] CORREO ENVIADO (ID: {response.json().get('id')})", flush=True)
        else:
            print(f"❌ [Background] Error Resend: {response.status_code} - {response.text}", flush=True)

    except Exception as e:
        print(f"❌ [Background] Error FATAL: {e}", flush=True)

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    print(f"📡 Recibida petición POST", flush=True)
    
    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario:
        return jsonify({"error": "Faltan datos"}), 400

    # Hilo en segundo plano (sigue siendo buena práctica)
    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    return jsonify({"estado": "en proceso"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')