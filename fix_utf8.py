#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess

# Comandos SQL con encoding UTF-8 correcto
updates = [
    "UPDATE personas SET nombre = 'Ana Martínez' WHERE id = 4;",
    "UPDATE personas SET nombre = 'Carlos Rodríguez' WHERE id = 3;",
    "UPDATE personas SET nombre = 'Juan Pérez' WHERE id = 1;",
    "UPDATE personas SET nombre = 'Luis Hernández' WHERE id = 5;",
    "UPDATE personas SET nombre = 'María González' WHERE id = 2;",
    "UPDATE personas SET nombre = 'Julián Peña' WHERE id = 6;"
]

sql_command = " ".join(updates)

# Ejecutar en el servidor remoto
cmd = [
    "ssh", "root@164.68.118.86",
    f"docker exec project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass project_ops -e \"{sql_command}\""
]

print("Corrigiendo caracteres UTF-8 en la base de datos...")
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

if result.returncode == 0:
    print("✅ Caracteres corregidos exitosamente")
else:
    print(f"❌ Error: {result.stderr}")

# Verificar
cmd_verify = [
    "ssh", "root@164.68.118.86",
    "docker exec project_ops_mysql mysql -uproject_ops_user -pproject_ops_pass --default-character-set=utf8mb4 project_ops -e 'SELECT id, nombre FROM personas;'"
]

print("\nVerificando resultados...")
result = subprocess.run(cmd_verify, capture_output=True, text=True, encoding='utf-8')
print(result.stdout)
