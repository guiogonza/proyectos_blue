"""
Ejemplo de uso de la API REST de Project Ops
"""
import requests
from requests.auth import HTTPBasicAuth
import json

# Configuración
API_URL = "http://164.68.118.86:8502"  # Cambiar a localhost:8502 para uso local
USERNAME = "admin@projectops.com"
PASSWORD = "admin123"

# Crear sesión con autenticación
session = requests.Session()
session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

def print_json(data):
    """Imprime JSON de forma legible"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

# ========== EJEMPLOS DE USO ==========

print("=" * 60)
print("1. HEALTH CHECK")
print("=" * 60)
response = session.get(f"{API_URL}/api/health")
print(f"Status: {response.status_code}")
print_json(response.json())

print("\n" + "=" * 60)
print("2. LISTAR PERSONAS")
print("=" * 60)
response = session.get(f"{API_URL}/api/personas")
personas = response.json()
print(f"Total de personas: {len(personas)}")
print_json(personas[:2])  # Mostrar las primeras 2

print("\n" + "=" * 60)
print("3. BUSCAR PERSONAS ACTIVAS")
print("=" * 60)
response = session.get(f"{API_URL}/api/personas", params={"activo": True})
print_json(response.json())

print("\n" + "=" * 60)
print("4. OBTENER PERSONA POR ID")
print("=" * 60)
response = session.get(f"{API_URL}/api/personas/1")
print_json(response.json())

print("\n" + "=" * 60)
print("5. LISTAR PROYECTOS")
print("=" * 60)
response = session.get(f"{API_URL}/api/proyectos")
proyectos = response.json()
print(f"Total de proyectos: {len(proyectos)}")
for p in proyectos:
    print(f"  - {p['nombre']} ({p['estado']})")

print("\n" + "=" * 60)
print("6. LISTAR SPRINTS DE UN PROYECTO")
print("=" * 60)
if proyectos:
    proyecto_id = proyectos[0]['id']
    response = session.get(f"{API_URL}/api/sprints", params={"proyecto_id": proyecto_id})
    sprints = response.json()
    print(f"Sprints del proyecto {proyectos[0]['nombre']}:")
    for s in sprints:
        print(f"  - {s['nombre']} ({s['estado']})")

print("\n" + "=" * 60)
print("7. LISTAR ASIGNACIONES DE UNA PERSONA")
print("=" * 60)
if personas:
    persona_id = personas[0]['id']
    response = session.get(f"{API_URL}/api/asignaciones", params={
        "persona_id": persona_id,
        "solo_activas": True
    })
    asignaciones = response.json()
    print(f"Asignaciones de {personas[0]['nombre']}:")
    print_json(asignaciones)

print("\n" + "=" * 60)
print("8. LISTAR USUARIOS (SOLO ADMIN)")
print("=" * 60)
response = session.get(f"{API_URL}/api/usuarios")
if response.status_code == 200:
    usuarios = response.json()
    print(f"Total de usuarios: {len(usuarios)}")
    for u in usuarios:
        print(f"  - {u['email']} ({u['rol_app']})")
elif response.status_code == 403:
    print("❌ Sin permisos (solo admin puede ver usuarios)")

print("\n" + "=" * 60)
print("9. ERROR HANDLING - Recurso no encontrado")
print("=" * 60)
response = session.get(f"{API_URL}/api/personas/99999")
print(f"Status: {response.status_code}")
if response.status_code == 404:
    print("❌ Recurso no encontrado")
    print_json(response.json())

print("\n" + "=" * 60)
print("10. DOCUMENTACIÓN INTERACTIVA")
print("=" * 60)
print(f"Swagger UI: {API_URL}/docs")
print(f"ReDoc: {API_URL}/redoc")
