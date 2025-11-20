from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
import socket # Necesario para el hack de IPv4

app = Flask(__name__)
CORS(app)

# CONFIGURACIÓN
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('EMAIL_USER')
# Quitamos los espacios de la contraseña por si acaso
SENDER_PASSWORD = os.environ.get('EMAIL_PASS', '').replace(' ', '') 
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

# --- HACK PARA FORZAR IPv4 ---
# Esto evita que Render intente conectar por IPv6 y se quede colgado
_orig_create_connection = socket.create_connection

def patched_create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    host, port = address
    # Si es gmail, forzamos la IP v4
    if host == SMTP_SERVER:
        try:
            # Buscamos solo la dirección IPv4 (family=socket.AF_INET)
            info = socket.getaddrinfo(host, port, socket.AF_INET)
            if info:
                host = info[0][4][0] # Usamos la IP numérica directamente
                address = (host, port)
        except Exception:
            pass # Si falla, dejamos que intente normal
            
    return _orig_create_connection(address, timeout, source_address)

socket.create_connection = patched_create_connection
# -----------------------------

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Conectando a Gmail (IPv4 Forzado)...")
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] CORREO ENVIADO EXITOSAMENTE a {destinatario}")

    except Exception as e:
        print(f"❌ [Background] Error FATAL enviando correo: {e}")

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario or not mensaje_texto:
        return jsonify({"error": "Faltan datos"}), 400

    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    return jsonify({"estado": "en proceso"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')