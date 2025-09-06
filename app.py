from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necesario para usar flash

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
        # Usar get() evita KeyError si el campo no existe
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
            return redirect(url_for('index'))
        else:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for('agregar'))

    return render_template('agregar.html')

if __name__ == '__main__':
    app.run(debug=True)
