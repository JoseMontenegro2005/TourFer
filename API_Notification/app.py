from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import threading

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN SENDGRID
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

# --- NUEVO: RUTA DESPERTADOR (Health Check) ---
@app.route('/', methods=['GET'])
def health_check():
    """
    Ruta ligera para despertar el servicio sin realizar acciones.
    """
    return jsonify({"estado": "activo", "servicio": "Notificaciones TourFer"}), 200
# ----------------------------------------------

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Enviando vía SendGrid a {destinatario}...", flush=True)
        
        url = "https://api.sendgrid.com/v3/mail/send"
        
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [
                {
                    "to": [{"email": destinatario}],
                    "subject": "Confirmación de Reserva - TourFer"
                }
            ],
            "from": {"email": FROM_EMAIL, "name": "TourFer Reservas"},
            "content": [
                {
                    "type": "text/plain",
                    "value": mensaje_texto
                }
            ]
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 202:
            print(f"✅ [Background] CORREO ENVIADO EXITOSAMENTE", flush=True)
        else:
            print(f"❌ [Background] Error SendGrid ({response.status_code}): {response.text}", flush=True)

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

    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    return jsonify({"estado": "en proceso"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')