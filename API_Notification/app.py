from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import threading

app = Flask(__name__)
CORS(app)

# --- CAMBIO 1: USAR PUERTO 465 (SSL) ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # <--- Antes era 587
SENDER_EMAIL = os.environ.get('EMAIL_USER')
SENDER_PASSWORD = os.environ.get('EMAIL_PASS')
API_KEY_SECRET = os.environ.get('NOTIFICACIONES_KEY')

def tarea_enviar_correo(destinatario, mensaje_texto):
    try:
        print(f"🔄 [Background] Iniciando envío a {destinatario}...")
        
        msg = MIMEMultipart()
        msg['From'] = f"TourFer Reservas <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Subject'] = "Confirmación de Reserva - TourFer"
        msg.attach(MIMEText(mensaje_texto, 'plain'))

        # --- CAMBIO 2: USAR SMTP_SSL ---
        # SMTP_SSL se conecta encriptado desde el inicio. Es más robusto para Render.
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        
        # server.starttls() <--- BORRAR O COMENTAR ESTA LÍNEA (No se usa con SSL/465)
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, destinatario, msg.as_string())
        server.quit()

        print(f"✅ [Background] Correo enviado exitosamente a {destinatario}")

    except Exception as e:
        print(f"❌ [Background] Error enviando correo: {e}")

@app.route('/enviar-correo', methods=['POST'])
def recibir_peticion():
    # (Esta parte del código no cambia, déjala igual)
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

    print(f"🚀 Petición recibida. Procesando envío para {destinatario}")
    return jsonify({"estado": "en proceso", "mensaje": "El correo se está enviando en segundo plano"}), 202

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5003))
    app.run(debug=True, port=port, host='0.0.0.0')