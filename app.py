from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para usar flash

# Función para inicializar la base de datos y crear tablas si no existen
def inicializar_db():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    
    # Crear tabla productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL
    )
    """)
    
    # Crear tabla ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        total REAL NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    # Insertar 20 productos si la tabla está vacía
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
        cursor.executemany("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)", productos)
    
    conn.commit()
    conn.close()

# Llamar a la función al iniciar la app
inicializar_db()

# Función para obtener ventas entre fechas
def obtener_ventas(inicio, fin):
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, producto, cantidad, total, fecha
        FROM ventas
        WHERE fecha BETWEEN ? AND ?
        ORDER BY fecha ASC
    """, (inicio, fin))
    ventas = cursor.fetchall()
    conn.close()
    return ventas

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Página About
@app.route("/about")
def about():
    return render_template("about.html")

# Página de reporte de ventas
@app.route('/reporte', methods=['GET', 'POST'])
def reporte():
    ventas = []
    if request.method == 'POST':
        inicio = request.form['inicio']
        fin = request.form['fin']
        ventas = obtener_ventas(inicio, fin)
    return render_template('reporte.html', ventas=ventas)

# Página para agregar un producto
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')

        if nombre and cantidad and precio:
            conn = sqlite3.connect('ventas.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                (nombre, cantidad, precio)
            )
            conn.commit()
            conn.close()

            flash("Producto agregado correctamente", "success")
            return redirect(url_for('productos'))
        else:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('agregar'))

    return render_template('agregar.html')

# Página para ver todos los productos
@app.route('/productos')
def productos():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos=productos)

# Página para ver ventas
@app.route('/ventas')
def ver_ventas():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas")  # Trae todas las ventas
    ventas = cursor.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

# Página de inventario
@app.route('/inventario')
def inventario():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return render_template('inventario.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)
