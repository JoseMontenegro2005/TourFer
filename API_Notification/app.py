from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/enviar-correo', methods=['POST'])
def enviar_notificacion():
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
    # IMPORTANTE: Usamos 5003 porque Reservas usa el 5002
    app.run(debug=True, port=5003)