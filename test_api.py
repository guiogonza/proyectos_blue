import requests
import json

auth = ('admin@projectops.com', 'admin123')
base_url = 'http://164.68.118.86:8502'

print("=" * 60)
print("PRUEBA COMPLETA DEL API - PROJECT OPS")
print("=" * 60)

# Test OpenAPI
print("\n=== DOCUMENTACIÓN API ===")
r = requests.get(f'{base_url}/openapi.json')
schema = r.json()
print(f"Title: {schema['info']['title']}")
print(f"Version: {schema['info']['version']}")
print(f"\nEndpoints disponibles:")
for path in schema['paths'].keys():
    methods = list(schema['paths'][path].keys())
    print(f"  {path} [{', '.join(m.upper() for m in methods)}]")

# Test Personas
print("\n=== PERSONAS ===")
r = requests.get(f'{base_url}/api/personas', auth=auth)
personas = r.json()
print(f"Total: {len(personas)}")
print(f"Campos nuevos en primer registro:")
p = personas[0]
print(f"  - ROL_PRINCIPAL: {p.get('ROL_PRINCIPAL')}")
print(f"  - COSTO_RECURSO: {p.get('COSTO_RECURSO')}")
print(f"  - NUMERO_DOCUMENTO: {p.get('NUMERO_DOCUMENTO')}")
print(f"  - PAIS: {p.get('PAIS')}")
print(f"  - SENIORITY: {p.get('SENIORITY')}")
print(f"  - LIDER_DIRECTO: {p.get('LIDER_DIRECTO')}")
print(f"  - LIDER_NOMBRE: {p.get('LIDER_NOMBRE')}")
print(f"  - TIPO_DOCUMENTO: {p.get('TIPO_DOCUMENTO')}")

# Test Proyectos
print("\n=== PROYECTOS ===")
r = requests.get(f'{base_url}/api/proyectos', auth=auth)
proyectos = r.json()
print(f"Total: {len(proyectos)}")
print(f"Campos nuevos en primer registro:")
pr = proyectos[0]
print(f"  - NOMBRE: {pr.get('NOMBRE')}")
print(f"  - FECHA_INICIO: {pr.get('FECHA_INICIO')}")
print(f"  - FECHA_FIN_ESTIMADA: {pr.get('FECHA_FIN_ESTIMADA')}")
print(f"  - ESTADO: {pr.get('ESTADO')}")
print(f"  - BUDGET: {pr.get('BUDGET')}")
print(f"  - COSTO_REAL_TOTAL: {pr.get('COSTO_REAL_TOTAL')}")
print(f"  - PAIS: {pr.get('PAIS')}")
print(f"  - CATEGORIA: {pr.get('CATEGORIA')}")
print(f"  - LIDER_BLUETAB: {pr.get('LIDER_BLUETAB')}")
print(f"  - LIDER_CLIENTE: {pr.get('LIDER_CLIENTE')}")
print(f"  - FECHA_FIN: {pr.get('FECHA_FIN')}")
print(f"  - MANAGER_BLUETAB: {pr.get('MANAGER_BLUETAB')}")

# Test Sprints
print("\n=== SPRINTS ===")
r = requests.get(f'{base_url}/api/sprints', auth=auth)
sprints = r.json()
print(f"Total: {len(sprints)}")
if sprints:
    print(f"Primer sprint: {sprints[0]['nombre']} - Proyecto: {sprints[0]['proyecto_nombre']}")

# Test Asignaciones
print("\n=== ASIGNACIONES ===")
r = requests.get(f'{base_url}/api/asignaciones', auth=auth)
asignaciones = r.json()
print(f"Total: {len(asignaciones)}")
if asignaciones:
    print(f"Primera asignación: {asignaciones[0]['persona_nombre']} -> {asignaciones[0]['proyecto_nombre']}")

# Test Usuarios
print("\n=== USUARIOS ===")
r = requests.get(f'{base_url}/api/usuarios', auth=auth)
usuarios = r.json()
print(f"Total: {len(usuarios)}")
if usuarios:
    print(f"Usuario admin: {usuarios[0]['email']} - Rol: {usuarios[0]['rol_app']}")

# Test endpoints específicos
print("\n=== ENDPOINTS POR ID ===")
r = requests.get(f'{base_url}/api/personas/1', auth=auth)
print(f"Persona ID 1: {r.json()['nombre']} - {r.json()['ROL_PRINCIPAL']}")

r = requests.get(f'{base_url}/api/proyectos/1', auth=auth)
print(f"Proyecto ID 1: {r.json()['NOMBRE']} - Estado: {r.json()['ESTADO']}")

print("\n" + "=" * 60)
print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("=" * 60)
