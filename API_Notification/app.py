from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN GMAIL (Usa variables de entorno en producción)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
# Pon aquí tu correo real
SENDER_EMAIL = os.environ.get('EMAIL_USER') 
SENDER_PASSWORD = os.environ.get('EMAIL_PASS') 
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

@app.route('/enviar-correo', methods=['POST'])
def enviar_notificacion():
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("❌ ERROR CRÍTICO: Faltan credenciales de correo en las variables de entorno.")
        return jsonify({"error": "Error de configuración del servidor"}), 500

    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario or not mensaje_texto:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        # 2. Crear el correo
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"

        # Cuerpo del mensaje
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        # 3. Conectar con Gmail y enviar
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Encriptación segura
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ Correo REAL enviado a {destinatario}")
        return jsonify({"estado": "enviado", "metodo": "SMTP Gmail"}), 200

    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')