from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde cualquier origen

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.json  # Obtener datos enviados desde el frontend
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    
    if not name or not email or not message:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400
    
    # Aquí podrías agregar lógica para enviar un correo o almacenar los datos
    
    return jsonify({"success": "Mensaje recibido correctamente"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usar el puerto asignado por Render
    app.run(host='0.0.0.0', port=port)