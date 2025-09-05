from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)

# Inicializar base de datos con datos de ejemplo
def inicializar_datos():
    db.create_all()
    if not Producto.query.first():
        productos_demo = [
            Producto(nombre="Arroz", precio=1.49),
            Producto(nombre="Leche", precio=1.09),
            Producto(nombre="Huevos", precio=2.11),
            Producto(nombre="Pan", precio=1.64),
            Producto(nombre="Manzanas", precio=2.07),
            Producto(nombre="Naranjas", precio=1.27),
            Producto(nombre="Tomates", precio=1.23),
            Producto(nombre="Cebollas", precio=1.04),
            Producto(nombre="Plátanos", precio=1.11),
            Producto(nombre="Pechuga de pollo", precio=5.65),
            Producto(nombre="Queso fresco", precio=6.15),
            Producto(nombre="Carne de res", precio=6.79),
        ]
        db.session.bulk_save_objects(productos_demo)
        db.session.commit()

with app.app_context():
    inicializar_datos()

# Página principal
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        if nombre and precio:
            try:
                nuevo_producto = Producto(nombre=nombre, precio=float(precio))
                db.session.add(nuevo_producto)
                db.session.commit()
            except ValueError:
                pass  # Podrías mostrar un mensaje de error si lo deseas
        return redirect(url_for('inicio'))

    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

# Eliminar producto
@app.route('/eliminar/<int:id>')
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('inicio'))

# Editar producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    producto = Producto.query.get_or_404(id)
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        if nombre and precio:
            try:
                producto.nombre = nombre
                producto.precio = float(precio)
                db.session.commit()
            except ValueError:
                pass
        return redirect(url_for('inicio'))
    return render_template('editar.html', producto=producto)

# Dashboard con estadísticas y gráfica
@app.route('/dashboard')
def dashboard():
    productos = Producto.query.all()
    labels = [p.nombre for p in productos]
    precios = [p.precio for p in productos]

    total = len(productos)
    promedio = round(sum(precios) / total, 2) if total > 0 else 0
    maximo = max(precios) if precios else 0
    minimo = min(precios) if precios else 0

    return render_template(
        'dashboard.html',
        labels=labels,
        precios=precios,
        total=total,
        promedio=promedio,
        maximo=maximo,
        minimo=minimo
    )

# Ejecutar servidor
if __name__ == '__main__':
    app.run(debug=True)