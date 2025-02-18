from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import os

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

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json  # Obtener datos enviados desde el frontend
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not name or not email or not message:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400
    
    # Aquí podrías agregar lógica para enviar un correo o almacenar los datos
    
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
        print("Error al enviar el correo:",e)
        return jsonify({"error": "Hubo un problema al enviar el correo"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto asignado por Render
    app.run(host='0.0.0.0', port=port)