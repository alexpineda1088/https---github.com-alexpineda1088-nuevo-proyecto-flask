from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from Conexion.conexion import get_connection
from datetime import date

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------------------
# Inicializar Base de Datos en MySQL
# ------------------------------
def inicializar_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                cantidad INT NOT NULL,
                precio DECIMAL(10,2) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                producto VARCHAR(50) NOT NULL,
                cantidad INT NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                fecha DATE NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                mail VARCHAR(100) NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            productos = [
                ('Leche', 50, 1.20), ('Pan', 100, 0.80), ('Huevos', 200, 0.10),
                ('Arroz', 150, 0.50), ('Frijoles', 80, 0.60), ('Azúcar', 120, 0.70),
                ('Sal', 100, 0.30), ('Aceite', 60, 2.00), ('Queso', 40, 3.50),
                ('Jabón', 70, 1.00), ('Shampoo', 50, 4.00), ('Cereal', 60, 2.50),
                ('Yogur', 80, 0.90), ('Mantequilla', 40, 1.50), ('Tomate', 100, 0.40),
                ('Lechuga', 90, 0.60), ('Pollo', 30, 5.00), ('Carne', 25, 6.00),
                ('Pescado', 20, 7.00), ('Café', 50, 3.00)
            ]
            cursor.executemany("INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)", productos)

        conn.commit()
    except Exception as e:
        print("Error al inicializar la base de datos:", e)
    finally:
        if conn:
            conn.close()

# ------------------------------
# Rutas principales
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# ------------------------------
# Productos
# ------------------------------
@app.route('/productos')
def productos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, cantidad, precio FROM productos")
    productos_db = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos_db=productos_db)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')

        if not nombre or not cantidad or not precio:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('agregar'))

        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except ValueError:
            flash("Cantidad y precio deben ser numéricos", "danger")
            return redirect(url_for('agregar'))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
                       (nombre, cantidad, precio))
        conn.commit()
        conn.close()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for('productos'))

    return render_template('agregar.html')

# ------------------------------
# Ventas
# ------------------------------
@app.route('/ventas')
def ver_ventas():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ventas")
    ventas = cursor.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

@app.route('/registrar_venta', methods=['POST'])
def registrar_venta():
    producto = request.form.get('producto')
    cantidad = request.form.get('cantidad')

    try:
        cantidad = int(cantidad)
    except ValueError:
        flash("Cantidad inválida", "danger")
        return redirect(url_for('productos'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT precio, cantidad FROM productos WHERE nombre = %s", (producto,))
    result = cursor.fetchone()

    if not result:
        flash("Producto no encontrado", "danger")
        conn.close()
        return redirect(url_for('productos'))

    precio_unitario, stock = result
    if cantidad > stock:
        flash("Cantidad insuficiente en inventario", "danger")
        conn.close()
        return redirect(url_for('productos'))

    total = precio_unitario * cantidad
    hoy = date.today()

    cursor.execute("INSERT INTO ventas (producto, cantidad, total, fecha) VALUES (%s, %s, %s, %s)",
                   (producto, cantidad, total, hoy))
    cursor.execute("UPDATE productos SET cantidad = cantidad - %s WHERE nombre = %s", (cantidad, producto))

    conn.commit()
    conn.close()
    flash("Venta registrada correctamente", "success")
    return redirect(url_for('ver_ventas'))

# ------------------------------
# Inicialización
# ------------------------------
if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)