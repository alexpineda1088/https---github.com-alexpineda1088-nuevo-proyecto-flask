import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='tu_contraseña',  # ← reemplaza con tu contraseña real
        database='mi_proyecto_desarrollo_web'
    )
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except mysql.connector.Error as err:
    print(f"❌ Error al conectar: {err}")