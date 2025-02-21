from flask import Blueprint, request, jsonify
import sqlite3

# Crear el Blueprint para el calendario
calendario_bp = Blueprint('calendario', __name__)

def init_db():
    with sqlite3.connect("citas.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            start TEXT NOT NULL
                          )''')
        conn.commit()

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
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, start FROM citas")  # Asegurar que se usa la tabla correcta
            citas = [{"id": row["id"], "title": row["title"], "start": row["start"]} for row in cursor.fetchall()]
        
        return jsonify(citas), 200
    
    except Exception as e:
        return jsonify({"error": f"Error al obtener citas: {str(e)}"}), 500

