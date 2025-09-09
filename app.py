from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import json
import csv

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Archivos de datos
TXT_FILE = "datos/datos.txt"
JSON_FILE = "datos/datos.json"
CSV_FILE = "datos/datos.csv"

# ------------------------------
# Inicializar Base de Datos
# ------------------------------
def inicializar_db():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()

    # Tabla productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)

    # Tabla ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)

    # Insertar productos iniciales si la tabla está vacía
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

# ------------------------------
# Inicializar Archivos TXT, JSON, CSV
# ------------------------------
def inicializar_archivos():
    os.makedirs("datos", exist_ok=True)
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, cantidad, precio FROM productos")
    productos = [{"nombre": p[0], "cantidad": p[1], "precio": p[2]} for p in cursor.fetchall()]
    conn.close()

    # TXT
    with open(TXT_FILE, "w", encoding="utf-8") as f:
        for p in productos:
            f.write(f"{p['nombre']},{p['precio']},{p['cantidad']}\n")

    # JSON
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=4, ensure_ascii=False)

    # CSV
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nombre", "precio", "cantidad"])
        for p in productos:
            writer.writerow([p["nombre"], p["precio"], p["cantidad"]])

# ------------------------------
# Funciones auxiliares
# ------------------------------
def sincronizar_archivos(nombre, precio, cantidad):
    # TXT
    with open(TXT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{precio},{cantidad}\n")

    # JSON
    productos_json = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            productos_json = json.load(f)
    productos_json.append({"nombre": nombre, "precio": float(precio), "cantidad": int(cantidad)})
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(productos_json, f, indent=4, ensure_ascii=False)

    # CSV
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre, precio, cantidad])

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

# ------------------------------
# Rutas principales
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/reporte', methods=['GET', 'POST'])
def reporte():
    ventas = []
    if request.method == 'POST':
        inicio = request.form['inicio']
        fin = request.form['fin']
        ventas = obtener_ventas(inicio, fin)
    return render_template('reporte.html', ventas=ventas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        cantidad = request.form.get('cantidad')
        precio = request.form.get('precio')
        if nombre and cantidad and precio:
            # Guardar en DB
            conn = sqlite3.connect('ventas.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                           (nombre, cantidad, precio))
            conn.commit()
            conn.close()
            # Sincronizar en archivos
            sincronizar_archivos(nombre, precio, cantidad)
            flash("Producto agregado correctamente", "success")
            return redirect(url_for('productos'))
        else:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('agregar'))
    return render_template('agregar.html')

@app.route('/productos')
def productos():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cantidad, precio FROM productos")
    productos_db = cursor.fetchall()
    conn.close()
    return render_template('productos.html', productos_db=productos_db)

@app.route('/ventas')
def ver_ventas():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ventas")
    ventas = cursor.fetchall()
    conn.close()
    return render_template('ventas.html', ventas=ventas)

@app.route('/inventario')
def inventario():
    # Productos desde DB
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cantidad, precio FROM productos")
    productos_db = cursor.fetchall()
    conn.close()

    # Productos desde archivos
    productos_txt, productos_json_file, productos_csv_file = [], [], []

    if os.path.exists(TXT_FILE):
        with open(TXT_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                nombre, precio, cantidad = linea.strip().split(',')
                productos_txt.append({"nombre": nombre, "precio": float(precio), "cantidad": int(cantidad)})

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            productos_json_file = json.load(f)

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                productos_csv_file.append({"nombre": row["nombre"], "precio": float(row["precio"]), "cantidad": int(row["cantidad"])})

    return render_template("inventario.html",
                           productos_db=productos_db,
                           productos_txt=productos_txt,
                           productos_json=productos_json_file,
                           productos_csv=productos_csv_file)

# ------------------------------
# Endpoints API para Archivos
# ------------------------------
@app.route('/api/productos/txt')
def api_productos_txt():
    productos = []
    if os.path.exists(TXT_FILE):
        with open(TXT_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                nombre, precio, cantidad = linea.strip().split(',')
                productos.append({"nombre": nombre, "precio": float(precio), "cantidad": int(cantidad)})
    return jsonify(productos)

@app.route('/api/productos/json')
def api_productos_json():
    productos = []
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            productos = json.load(f)
    return jsonify(productos)

@app.route('/api/productos/csv')
def api_productos_csv():
    productos = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                productos.append({"nombre": row["nombre"], "precio": float(row["precio"]), "cantidad": int(row["cantidad"])})
    return jsonify(productos)
@app.route('/inventario_moderno')
def inventario_moderno():
    conn = sqlite3.connect('ventas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, cantidad, precio FROM productos")
    productos_db = cursor.fetchall()
    conn.close()

    # Archivos TXT, JSON, CSV
    productos_txt = []
    productos_json = []
    productos_csv = []
    # ... carga los archivos como en tu código actual

    return render_template("inventario_datatables.html",
                           productos_db=productos_db,
                           productos_txt=productos_txt,
                           productos_json=productos_json,
                           productos_csv=productos_csv)

# ------------------------------
# Inicialización
# ------------------------------
inicializar_db()
inicializar_archivos()

if __name__ == '__main__':
    app.run(debug=True)
