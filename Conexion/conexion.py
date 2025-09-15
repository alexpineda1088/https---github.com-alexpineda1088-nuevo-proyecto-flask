import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='tu_contraseña',
    database='mi_proyecto_desarrollo_web'
)

print("Conexión exitosa")
conn.close()