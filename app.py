from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import re # Importar el módulo de expresiones regulares
import requests
from routes_calendario import calendario_bp, init_db

# Clave secreta reCATPCHA (Guardar como variable de entorno)

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde cualquier origen

init_db()

# Registrar el Blueprint de calendario
app.register_blueprint(calendario_bp)

# Configuración del servidor de correo (Usaremos Gmail como ejemplo)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")  # Correo del remitente
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")  # Contraseña del remitente
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")  # Mismo correo del remitente

mail = Mail(app)

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")

def verify_recaptcha(response_token):
    """Verifica si el reCAPTCHA es válido con Google."""
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": response_token}
    response = requests.post(url, data=data).json()
        
    return response.get("success", False)

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json  # Obtener datos enviados desde el frontend
    
    recaptcha_token = data.get('recaptchaToken')
    # Validar reCAPTCHA antes de continuar
    if not recaptcha_token or not verify_recaptcha(recaptcha_token):
        return jsonify({"error": "reCAPTCHA inválido o no verificado"}), 400
    
    name = data.get('name','').strip() # Obtener el nombre y eliminar espacios al inicio y al final
    email = data.get('email','').strip()
    message = data.get('message','').strip()
    
    if not name or not email or not message:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if len(name) < 2 or len(name) > 50:
        return jsonify({"error": "El nombre debe tener entre 2 y 50 caracteres."}), 400

    if not is_valid_email(email):
        return jsonify({"error": "El correo electrónico no es válido."}), 400

    if len(message) < 4 or len(message) > 1000:
        return jsonify({"error": "El mensaje debe tener entre 4 y 1000 caracteres."}), 400

    # Crear el correo
    msg = Message(
        subject=f"Nuevo mensaje de {name}",
        sender=email, # Quien envia el mensaje
        recipients=[os.environ.get("MAIL_USERNAME")],  # Quien recibe el mensaje
        body=f"Nombre: {name}\nCorreo: {email}\nMensaje: {message}"
    )
    
    try: 
        mail.send(msg)  # Enviar el correo
        return jsonify({"success": "Correo enviado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Hubo un problema al enviar el correo: {str(e)}"}), 500
    

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto asignado por Render
    app.run(host='0.0.0.0', port=port)