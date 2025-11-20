from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN GMAIL - PUERTO 587 (TLS)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASSWORD = os.environ.get('EMAIL_PASS')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

def tarea_enviar_correo(destinatario, mensaje_texto):
    """
    Función que se ejecuta en segundo plano.
    Tiene su propio manejo de errores para no afectar la respuesta HTTP.
    """
    try:
        print(f"🔄 [Background] Iniciando conexión a Gmail (Puerto {SMTP_PORT}) para {destinatario}...")
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        # Conexión SMTP estándar con timeout de 60 segundos
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60)
        
        # Protocolo de seguridad TLS para puerto 587
        server.ehlo() 
        server.starttls() 
        server.ehlo()

        # Login y envío
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] Correo enviado exitosamente a {destinatario}")

    except Exception as e:
        print(f"❌ [Background] Error enviando correo: {e}")

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    # 1. Verificación de Seguridad
    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario or not mensaje_texto:
        return jsonify({"error": "Faltan datos"}), 400

    # 2. Lanzar el hilo en segundo plano
    # Esto permite responder al usuario INMEDIATAMENTE mientras el correo se envía después
    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    print(f"🚀 Petición aceptada. Procesando envío en segundo plano.")
    return jsonify({"estado": "en proceso", "mensaje": "El correo se está enviando"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')