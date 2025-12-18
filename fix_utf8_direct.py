#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir doble encoding UTF-8 en nombres de personas
"""
import pymysql
import sys

# Datos correctos
nombres_correctos = {
    1: 'Juan Pérez',
    2: 'María González', 
    3: 'Carlos Rodríguez',
    4: 'Ana Martínez',
    5: 'Luis Hernández',
    6: 'Julián Peña'
}

print("Conectando a la base de datos en el servidor remoto...")
print("Nota: Asegúrate de tener un túnel SSH abierto en el puerto 3310")
print("Comando: ssh -L 3310:localhost:3310 root@164.68.118.86 -N")
print()

try:
    # Conectar usando el túnel SSH
    conn = pymysql.connect(
        host='localhost',
        port=3310,
        user='project_ops_user',
        password='project_ops_pass',
        database='project_ops',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✅ Conexión exitosa")
    
    with conn.cursor() as cursor:
        # Leer datos actuales
        cursor.execute("SELECT id, nombre FROM personas")
        personas = cursor.fetchall()
        
        print("\n📊 Nombres actuales en BD:")
        for p in personas:
            print(f"  ID {p['id']}: {p['nombre']}")
        
        # Actualizar nombres
        print("\n🔄 Actualizando nombres...")
        for persona_id, nombre_correcto in nombres_correctos.items():
            sql = "UPDATE personas SET nombre = %s WHERE id = %s"
            cursor.execute(sql, (nombre_correcto, persona_id))
            print(f"  ✓ ID {persona_id}: {nombre_correcto}")
        
        conn.commit()
        
        # Verificar
        print("\n✅ Verificando cambios...")
        cursor.execute("SELECT id, nombre FROM personas")
        personas = cursor.fetchall()
        
        for p in personas:
            print(f"  ID {p['id']}: {p['nombre']}")
    
    conn.close()
    print("\n🎉 Corrección completada exitosamente")
    
except pymysql.Error as e:
    print(f"\n❌ Error de base de datos: {e}")
    print("\n💡 Asegúrate de:")
    print("   1. Tener un túnel SSH activo: ssh -L 3310:localhost:3310 root@164.68.118.86 -N")
    print("   2. El puerto 3310 está expuesto en docker-compose.yml")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
