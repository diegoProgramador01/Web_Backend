from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import re # Importar el módulo de expresiones regulares
import requests

# Clave secreta reCATPCHA (Guardar como variable de entorno)

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde cualquier origen

# Configuración del servidor de correo (Usaremos Gmail como ejemplo)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")  # Correo del remitente
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")  # Contraseña del remitente
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")  # Mismo correo del remitente

mail = Mail(app)

def write_log(message):
    with open("logs.txt", "a") as log_file:
        log_file.write(f"{message}\n")

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")

def verify_recaptcha(response_token):
    """Verifica si el reCAPTCHA es válido con Google."""
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response_token}
    response = requests.post(url, data=data).json()
    
    write_log(f"🔍 Respuesta de reCAPTCHA: {response}")
        
    return response.get("success", False)

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json  # Obtener datos enviados desde el frontend
    write_log(f"📩 Datos recibidos en backend: {data}")
    recaptcha_token = data.get('recaptchaToken')
    
    # Validar reCAPTCHA antes de continuar
    if not recaptcha_token or not verify_recaptcha(recaptcha_token):
        write_log("❌ reCAPTCHA inválido o no verificado")
        return jsonify({"error": "reCAPTCHA inválido o no verificado"}), 400
    
    name = data.get('name','').strip() # Obtener el nombre y eliminar espacios al inicio y al final
    email = data.get('email','').strip()
    message = data.get('message','').strip()
    write_log(f"🔍 Nombre: {name}, Email: {email}, Mensaje: {message}")
    
    
    
    if not name or not email or not message:
        write_log("❌ Error: Todos los campos son obligatorios")
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if len(name) < 2 or len(name) > 50:
        write_log("❌ Error: El nombre no tiene la longitud permitida")
        return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres."}), 400

    if not is_valid_email(email):
        write_log("❌ Error: Correo no válido")
        return jsonify({"error": "El correo electrónico no es válido."}), 400

    if len(message) < 10 or len(message) > 1000:
        write_log("❌ Error: Mensaje no tiene la longitud permitida")
        return jsonify({"error": "El mensaje debe tener entre 10 y 1000 caracteres."}), 400

    # Crear el correo
    msg = Message(
        subject=f"Nuevo mensaje de {name}",
        sender=email, # Quien envia el mensaje
        recipients=[os.environ.get("MAIL_USERNAME")],  # Quien recibe el mensaje
        body=f"Nombre: {name}\nCorreo: {email}\nMensaje: {message}"
    )
    
    try: 
        mail.send(msg)  # Enviar el correo
        write_log("✅ Correo enviado correctamente")
        return jsonify({"success": "Correo enviado correctamente"}), 200
    except Exception as e:
        write_log(f"❌ Error al enviar el correo: {e}")
        return jsonify({"error": "Hubo un problema al enviar el correo"}), 500
    
# Ruta para ver los logs en el navegador
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open("logs.txt", "r") as log_file:
            return log_file.read(), 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return "No hay logs aún.", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto asignado por Render
    app.run(host='0.0.0.0', port=port)