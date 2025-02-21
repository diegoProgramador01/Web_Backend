from flask import Blueprint, request, jsonify
import sqlite3

# Crear el Blueprint para el calendario
calendario_bp = Blueprint('calendario', __name__)

# Función para conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect("citas.db")
    conn.row_factory = sqlite3.Row
    return conn

# Ruta para crear una nueva cita
@calendario_bp.route('/crear-cita', methods=['POST'])
def crear_cita():
    data = request.json
    title = data.get("title")
    start = data.get("start")

    if not title or not start:
        return jsonify({"error": "Faltan datos"}), 400

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO citas (title, start) VALUES (?, ?)", (title, start))
        conn.commit()

    return jsonify({"title": title, "start": start})

# Ruta para obtener todas las citas
@calendario_bp.route('/obtener-citas', methods=['GET'])
def obtener_citas():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, start FROM citas")
        citas = [{"title": row["title"], "start": row["start"]} for row in cursor.fetchall()]
    
    return jsonify(citas)
