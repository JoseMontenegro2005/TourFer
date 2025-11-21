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

# --- CONFIGURACIÓN ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASSWORD = os.environ.get('EMAIL_PASS', '').replace(' ', '')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

# --- HACK IPv4 ---
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
# -----------------

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Conectando a Gmail (465 SSL + IPv4)...", flush=True)
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        # Usamos SMTP_SSL directo
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=60)
        
        # Login
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] CORREO ENVIADO A: {destinatario}", flush=True)

    except Exception as e:
        print(f"❌ [Background] Error FATAL: {e}", flush=True)

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    print(f"📡 Recibida petición POST en /enviar-correo", flush=True) # Log de entrada
    
    api_key_recibida = request.headers.get('X-Notification-Key')
    if api_key_recibida != API_KEY_SECRET:
        print(f"🚫 Acceso denegado: Key incorrecta", flush=True)
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    destinatario = data.get('email')
    mensaje_texto = data.get('mensaje')

    if not destinatario:
        print("⚠️ Falta destinatario", flush=True)
        return jsonify({"error": "Faltan datos"}), 400

    # Iniciar hilo
    hilo = threading.Thread(target=tarea_enviar_correo, args=(destinatario, mensaje_texto))
    hilo.start()

    return jsonify({"estado": "en proceso"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')