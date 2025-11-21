from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading
import socket

app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN: VOLVEMOS AL 587 ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASSWORD = os.environ.get('EMAIL_PASS', '').replace(' ', '')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

# --- HACK IPv4 (MANTENER SIEMPRE EN RENDER) ---
_orig_create_connection = socket.create_connection

def patched_create_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
    host, port = address
    if host == SMTP_SERVER:
        try:
            info = socket.getaddrinfo(host, port, socket.AF_INET)
            if info:
                host = info[0][4][0]
                address = (host, port)
        except Exception:
            pass
    return _orig_create_connection(address, timeout, source_address)

socket.create_connection = patched_create_connection
# ----------------------------------------------

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Conectando a Gmail (Puerto 587 + IPv4)...", flush=True)
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        # 1. Conexión inicial sin SSL
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.set_debuglevel(0) # Cambiar a 1 si quieres ver logs detallados de protocolo
        
        # 2. Negociación TLS (Encriptación)
        server.ehlo()
        server.starttls() 
        server.ehlo()

        # 3. Login
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] CORREO ENVIADO EXITOSAMENTE a {destinatario}", flush=True)

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