from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app)

API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY', 'clave_segura_local_123')

@app.route('/enviar-correo', methods=['POST'])
def enviar_notificacion():
    api_key_recibida = request.headers.get('X-Notification-Key')
    
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado: API Key inválida"}), 403
    data = request.get_json()
    email = data.get('email')
    mensaje = data.get('mensaje')

    if not email or not mensaje:
        return jsonify({"error": "Faltan datos"}), 400

    # Simulamos el proceso de envío
    print("------------------------------------------------")
    print(f"📧 [NUEVO CORREO] Enviando a: {email}")
    print(f"📝 Mensaje: {mensaje}")
    time.sleep(1.5) # Simulamos que tarda un poco en enviar
    print("✅ Correo enviado exitosamente.")
    print("------------------------------------------------")

    return jsonify({"estado": "enviado"}), 200

if __name__ == '__main__':
    # En Render, el puerto también se lee del entorno
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')