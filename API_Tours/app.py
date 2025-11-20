from flask import Flask, jsonify, request
from functools import wraps
from config import Config, get_api_key
from db import get_db_connection # <-- CAMBIO: Importamos la función de conexión
import psycopg2.extras # <-- CAMBIO: Necesario para diccionarios

app = Flask(__name__)

# (Ya no usamos init_mysql aquí, la conexión se crea por petición)

# --- DECORADOR DE SEGURIDAD ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == get_api_key():
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Acceso no autorizado"}), 401
    return decorated_function

# --- RUTAS PÚBLICAS ---

@app.route('/tours', methods=['GET'])
def get_all_tours():
    conn = get_db_connection()
    # Usamos RealDictCursor para recibir diccionarios, no tuplas
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT * FROM tours")
    tours = cur.fetchall()
    
    cur.close()
    conn.close()
    return jsonify(tours)

@app.route('/tours/<int:id>', methods=['GET'])
def get_tour_by_id(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT * FROM tours WHERE id = %s", (id,))
    tour = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if tour:
        return jsonify(tour)
    return jsonify({"error": "Tour no encontrado"}), 404

@app.route('/guias', methods=['GET'])
def get_all_guias():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT id, nombre, email, biografia FROM guias")
    guias = cur.fetchall()
    
    cur.close()
    conn.close()
    return jsonify(guias)

# --- RUTAS PROTEGIDAS (Escritura) ---

@app.route('/tours', methods=['POST'])
@require_api_key
def create_tour():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # CAMBIO IMPORTANTE: PostgreSQL usa 'RETURNING id' para obtener el ID creado
        cur.execute(
            """
            INSERT INTO tours (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, guia_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (data['nombre'], data['destino'], data['descripcion'], data['duracion_horas'], 
             data['precio'], data['cupos_disponibles'], data.get('guia_id'))
        )
        conn.commit()
        
        # Obtenemos el ID devuelto por el RETURNING
        new_id = cur.fetchone()['id']
        
        cur.close()
        conn.close()
        return jsonify({"mensaje": "Tour creado exitosamente", "id": new_id}), 201
        
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/tours/<int:id>', methods=['PUT'])
@require_api_key
def update_tour(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE tours
        SET nombre = %s,
            destino = %s,
            descripcion = %s,
            duracion_horas = %s,
            precio = %s,
            cupos_disponibles = %s,
            guia_id = %s
        WHERE id = %s
    """, (data['nombre'], data['destino'], data['descripcion'], data['duracion_horas'], 
          data['precio'], data['cupos_disponibles'], data.get('guia_id'), id))
    
    conn.commit()
    rows_affected = cur.rowcount
    cur.close()
    conn.close()
    
    if rows_affected == 0:
        return jsonify({"error": "Tour no encontrado"}), 404
        
    return jsonify({"mensaje": "Tour actualizado exitosamente"})

@app.route('/tours/<int:id>', methods=['DELETE'])
@require_api_key
def delete_tour(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM tours WHERE id = %s", (id,))
    conn.commit()
    rows_affected = cur.rowcount
    
    cur.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({"error": "Tour no encontrado para eliminar"}), 404

    return jsonify({"mensaje": "Tour eliminado exitosamente"})

@app.route('/tours/<int:id>/cupos', methods=['PATCH'])
@require_api_key
def update_tour_cupos(id):
    data = request.get_json()
    conn = get_db_connection()
    # Usamos RealDictCursor para leer los cupos actuales fácilmente
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute("SELECT cupos_disponibles FROM tours WHERE id = %s", (id,))
        tour = cur.fetchone()

        if not tour:
            cur.close()
            conn.close()
            return jsonify({"error": "Tour no encontrado"}), 404

        cupos_actuales = tour['cupos_disponibles']
        cantidad = data['cantidad']
        accion = data['accion']

        if accion == 'decrementar':
            if cupos_actuales >= cantidad:
                nuevos_cupos = cupos_actuales - cantidad
            else:
                cur.close()
                conn.close()
                return jsonify({"error": "No hay suficientes cupos disponibles"}), 409
        elif accion == 'incrementar':
            nuevos_cupos = cupos_actuales + cantidad
        else:
            cur.close()
            conn.close()
            return jsonify({"error": "Acción no válida"}), 400

        # Ejecutamos el update
        cur.execute("UPDATE tours SET cupos_disponibles = %s WHERE id = %s", (nuevos_cupos, id))
        conn.commit()
        
        cur.close()
        conn.close()
        return jsonify({"mensaje": f"Cupos actualizados. Nuevo total: {nuevos_cupos}"})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/guias', methods=['POST'])
@require_api_key
def create_guia():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        cur.execute(
            "INSERT INTO guias (nombre, email) VALUES (%s, %s) RETURNING id", 
            (data['nombre'], data['email'])
        )
        conn.commit()
        new_id = cur.fetchone()['id']
        
        cur.close()
        conn.close()
        return jsonify({"mensaje": "Guía creado exitosamente", "id": new_id}), 201
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": f"Error al crear guía: {str(e)}"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)