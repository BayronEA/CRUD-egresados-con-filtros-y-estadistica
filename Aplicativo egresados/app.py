from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = '2024' 

# Configuración de la base de datos MySQL (reemplaza con tus propias credenciales)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin1234'
app.config['MYSQL_DB'] = 'universidad_pamplona'

SUPERUSER_USERNAME = 'unipamplona'
SUPERUSER_PASSWORD = 'root'

mysql = MySQL(app)



def usuario_existe(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    return result is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cur = mysql.connection.cursor()

    # Consulta SQL para obtener el hash de la contraseña almacenado
    cur.execute("SELECT password_hash FROM usuarios WHERE username = %s", (username,))
    result = cur.fetchone()

    # Verificación básica de la contraseña (sin hashing)
    if result and result[0] == password:
        #flash('Inicio de sesión exitoso. ¡Bienvenido, {}!'.format(username), 'success')
        cur.close()
        return redirect(url_for('main'))
        
    else:
        flash('Nombre de usuario o contraseña incorrectos.', 'error')
        cur.close()
        return redirect(url_for('index'))
    
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/crearusuario', methods=['GET', 'POST'])
def crearusuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if usuario_existe(username):
            flash('El usuario {} ya existe. Por favor, elige otro nombre de usuario.'.format(username), 'error')

        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            cur.close()

            flash('Usuario {} ha sido creado exitosamente.'.format(username), 'success')

    return render_template('crearusuario.html')


@app.route('/verificar_superusuario', methods=['POST'])
def verificar_superusuario():
    data = request.get_json()
    input_username = data.get('username')
    input_password = data.get('password')

    # Verifica las credenciales del superusuario
    if input_username == SUPERUSER_USERNAME and input_password == SUPERUSER_PASSWORD:
        # Devuelve una respuesta JSON indicando una verificación exitosa
        return jsonify(success=True)
    else:
        # Devuelve una respuesta JSON indicando una verificación fallida
        return jsonify(success=False)
    
@app.route('/visualizardatos')
def visualizar_datos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM egresados")
    egresados = cur.fetchall()
    cur.close()
    return render_template('visualizardatos.html', egresados=egresados)

@app.route('/crearegresado')
def crearegresado():
    return render_template('agregardatosegresados.html')

@app.route('/guardaregresado', methods=['POST'])
def guardar_egresado():
    if request.method == 'POST':
        # captura los datos del formulario
        id = request.form['id']
        nombre = request.form['nombre']
        carrera = request.form['carrera']
        anio_graduacion = request.form['anio_graduacion']
        salario_promedio = request.form['salario_promedio']
        continua_estudios = 1 if 'continua_estudios' in request.form else 0
        tiempo_empleo = request.form['tiempo_empleo']
        
        # abre una conexión a la base de datos
        cur = mysql.connection.cursor()

        # Verifica si el ID ya existe en la base de datos
        cur.execute("SELECT * FROM egresados WHERE id = %s", (id,))
        existing_egresado = cur.fetchone()

        if existing_egresado:
            flash('El egresado con ID {} ya está registrado.'.format(id), 'error')
        else:
            # ejecuta la consulta SQL para insertar los datos en la tabla de egresados
            cur.execute("INSERT INTO egresados (id, nombre, carrera, ano_graduacion, salario_promedio, continua_estudios, tiempo_conseguir_empleo) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id, nombre, carrera, anio_graduacion, salario_promedio, continua_estudios, tiempo_empleo))

            # confirma la operación de inserción en la base de datos
            mysql.connection.commit()
            # Muestra un mensaje flash de éxito
            flash('Datos del egresado guardados exitosamente.', 'success')

        cur.close()
        # Redirige a la misma página
        return render_template('agregardatosegresados.html')
    
@app.route('/filtrar_egresados', methods=['POST'])
def filtrar_egresados():
    data = request.json
    carrera = data.get('carrera')
    graduacion = data.get('graduacion')
    salario_min = data.get('salarioMin')
    salario_max = data.get('salarioMax')
    continuacion = data.get('continuacion')
    tiempo_empleo = data.get('tiempoEmpleo')

    # Consulta SQL base para filtrar los datos
    query = "SELECT * FROM egresados WHERE 1=1"

    # Agregar cláusulas WHERE según los filtros proporcionados
    if carrera:
        query += " AND carrera = '{}'".format(carrera)
    if graduacion:
        query += " AND ano_graduacion = {}".format(graduacion)
    if salario_min:
        query += " AND salario_promedio >= {}".format(salario_min)
    if salario_max:
        query += " AND salario_promedio <= {}".format(salario_max)
    if continuacion:
        query += " AND continua_estudios = {}".format(continuacion)
    if tiempo_empleo:
        query += " AND tiempo_conseguir_empleo = {}".format(tiempo_empleo)

    # Ejecutar la consulta SQL
    cur = mysql.connection.cursor()
    cur.execute(query)
    egresados_filtrados = cur.fetchall()
    cur.close()
    # Imprimir los datos filtrados en la consola
    # Convertir los resultados a un formato JSON y devolverlos como respuesta
    return jsonify(egresados_filtrados)

# @app.route('/graficar', methods=['POST'])
# def graficar():
#     data = request.json
#     # Aquí procesa los datos según sea necesario y devuelve los datos para el gráfico
#     return jsonify(data)
    
    
if __name__ == '__main__':
    app.run(debug=True)
