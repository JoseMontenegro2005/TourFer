from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading # <--- LA CLAVE MÁGICA

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN GMAIL
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASSWORD = os.environ.get('EMAIL_PASS')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

def tarea_enviar_correo(destinatario, mensaje_texto):
    """
    Esta función se ejecutará en segundo plano.
    Aquí es donde ocurre la conexión lenta con Gmail.
    """
    try:
        print(f"🔄 [Background] Iniciando envío a {destinatario}...")
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) # Timeout interno de conexión
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] Correo enviado exitosamente a {destinatario}")

    except Exception as e:
        # Como esto corre en segundo plano, si falla solo lo vemos en los logs
        # El usuario ya recibió su confirmación en pantalla
        print(f"❌ [Background] Error enviando correo: {e}")

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    # 1. Seguridad
    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario or not mensaje_texto:
        return jsonify({"error": "Faltan datos"}), 400

    # 2. AQUÍ ESTÁ EL TRUCO:
    # Creamos un hilo que ejecutará la función 'tarea_enviar_correo'
    # y le pasamos los datos (args).
    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    # 3. Respondemos INMEDIATAMENTE al usuario, sin esperar a Gmail
    print(f"🚀 Petición recibida. Procesando envío en segundo plano para {destinatario}")
    return jsonify({"estado": "en proceso", "mensaje": "El correo se está enviando en segundo plano"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')