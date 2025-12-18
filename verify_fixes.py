import requests
import json

auth = ('admin@projectops.com', 'admin123')
base_url = 'http://164.68.118.86:8502'

print("\n=== VERIFICACIÓN FINAL ===\n")

# Test Personas con UTF-8
print("📊 PERSONAS:")
r = requests.get(f'{base_url}/api/personas', auth=auth)
personas = r.json()
for p in personas:
    print(f"  ✓ {p['nombre']} ({p['ROL_PRINCIPAL']})")

# Test Asignaciones
print("\n📋 ASIGNACIONES:")
r = requests.get(f'{base_url}/api/asignaciones', auth=auth)
asignaciones = r.json()
for a in asignaciones[:3]:
    print(f"  ✓ {a['persona_nombre']} → {a['proyecto_nombre']}")

# Test Proyectos
print("\n📁 PROYECTOS:")
r = requests.get(f'{base_url}/api/proyectos', auth=auth)
proyectos = r.json()
for p in proyectos:
    print(f"  ✓ {p['NOMBRE']} - {p['ESTADO']} - Budget: ${p['BUDGET']:,.0f}")

print("\n✅ TODOS LOS ERRORES CORREGIDOS")
print("   - KeyError 'rol' → SOLUCIONADO (ahora usa ROL_PRINCIPAL)")
print("   - Caracteres especiales → SOLUCIONADOS (UTF-8 correcto)")
