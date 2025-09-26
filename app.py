from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__, template_folder='templates')

# Configuración de la base de datos
DB_HOST = 'dpg-d32a982dbo4c73a9n5u0-a'
DB_NAME = 'personasdb_6c36'
DB_USER = 'personasdb_6c36_user'
DB_PASSWORD = '8gHgOWeJ1X2stnZPFFlC6CgFfdjdRmTI'


def conectar_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
        return conn
    except psycopg2.Error as e:
        print("Error al conectar a la base de datos:", e)


def crear_persona(dni, nombre, apellido, direccion, telefono):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO personas (dni, nombre, apellido, direccion, telefono) 
        VALUES (%s, %s, %s, %s, %s)
    """, (dni, nombre, apellido, direccion, telefono))
    conn.commit()
    conn.close()


def obtener_registros():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""
        SELECT id, dni, nombre, apellido, direccion, telefono 
        FROM personas 
        ORDER BY apellido
    """)
    registros = cursor.fetchall()
    conn.close()
    return registros


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registrar', methods=['POST'])
def registrar():
    try:
        # Obtener y validar datos
        dni = request.form.get('dni', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()

        # Validaciones del servidor
        if not dni or not nombre or not apellido:
            return jsonify({'error': 'Los campos DNI, nombre y apellido son requeridos'}), 400

        if not dni.isdigit() or len(dni) < 7 or len(dni) > 8:
            return jsonify({'error': 'DNI inválido'}), 400

        # Crear persona
        crear_persona(dni, nombre, apellido, direccion if direccion else None, telefono if telefono else None)

        # Si es una petición AJAX, devolver JSON
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'success': True, 'message': 'Registro exitoso'})

        # Si es una petición normal, redirigir
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error al registrar: {e}")
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({'error': 'Error interno del servidor'}), 500
        return redirect(url_for('index'))


@app.route('/administrar')
def administrar():
    registros = obtener_registros()
    return render_template('administrar.html', registros=registros)


@app.route('/eliminar/<dni>', methods=['POST'])
def eliminar_registro(dni):
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personas WHERE dni = %s", (dni,))
    conn.commit()
    conn.close()
    return redirect(url_for('administrar'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
