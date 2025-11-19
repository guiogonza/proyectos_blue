import pymysql
import bcrypt
from datetime import datetime

# Conectar a la base de datos
conn = pymysql.connect(
    host='mysql',
    user='project_ops_user',
    password='project_ops_pass',
    database='project_ops'
)

cursor = conn.cursor()

# Crear hash de la contraseña
password = 'admin123'
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
hashed_str = hashed.decode('utf-8')

# Insertar usuario admin
sql = """
INSERT INTO usuarios (email, hash_password, rol_app, activo, created_at)
VALUES (%s, %s, %s, %s, %s)
"""

cursor.execute(sql, ('admin@projectops.com', hashed_str, 'admin', 1, datetime.now()))
conn.commit()

print(f"Usuario admin creado exitosamente")
print(f"Email: admin@projectops.com")
print(f"Password: admin123")
print(f"Rol: admin")

cursor.close()
conn.close()
