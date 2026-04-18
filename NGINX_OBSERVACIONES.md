# Nginx - Observaciones del incidente (2026-04-18)

## Resumen
Se presento error 404 en la ruta publica:
- http://164.68.118.86/colombia

El backend y los contenedores de Project Ops estaban activos, pero Nginx no tenia el enrutamiento correcto para ese prefijo en el server block que realmente estaba tomando las peticiones.

## Causa raiz
1. Habia multiples sitios Nginx escuchando en puerto 80 con el mismo host/IP.
2. El archivo activo para `server_name 164.68.118.86` fue `evaluaciones-ip.conf`.
3. Ese archivo no tenia las rutas de Project Ops (`/colombia`, `/colombia-api`, `/peru`, `/peru-api`).
4. Nginx intento resolver `/colombia` como archivo estatico en `/usr/share/nginx/html/colombia` y respondio 404.

## Evidencia observada
- En `error.log` aparecio:
  - `open() "/usr/share/nginx/html/colombia" failed (2: No such file or directory)`
- Los contenedores estaban arriba:
  - `project_ops_app` (8501)
  - `project_ops_api` (8502)
  - `project_ops_app_peru` (8510)
  - `project_ops_api_peru` (8511)

## Correccion aplicada
1. Se agregaron rutas de Project Ops dentro del server block activo en `evaluaciones-ip.conf`:
   - `/colombia` -> `127.0.0.1:8501`
   - `/colombia-api` -> `127.0.0.1:8502`
   - `/peru` -> `127.0.0.1:8510`
   - `/peru-api` -> `127.0.0.1:8511`
2. Se aplico fix para subrutas de Streamlit en Login:
   - `.../Login/_stcore/...` reescribe a `.../_stcore/...`
3. Se valido y recargo Nginx:
   - `nginx -t`
   - `systemctl reload nginx`

## Resultado
- `http://164.68.118.86/colombia/` responde y carga pantalla de login.
- Se elimino el 404 principal por falta de location.
- Se corrigieron 404 de `_stcore/health` y `_stcore/host-config` en subrutas internas de Streamlit.

## Warnings detectados (no bloqueantes)
Durante `nginx -t` se observaron warnings en otros sitios:
- `duplicate MIME type "text/html"` en `gitea-bare-ip`
- `conflicting server name` para algunos hosts en `:80`

Estos warnings no bloquearon el arreglo de Project Ops, pero conviene limpiar configuraciones duplicadas para evitar futuras colisiones.

## Recomendaciones operativas
1. Mantener una sola definicion principal para `server_name 164.68.118.86` en puerto 80.
2. Evitar repetir `server_name`/`listen 80` sin una estrategia clara de enrutamiento.
3. Versionar todos los archivos de Nginx criticos en este repositorio.
4. Despues de cada cambio:
   - `nginx -t`
   - `systemctl reload nginx`
   - prueba rapida de URLs criticas (`/colombia`, `/peru`, `/colombia-api/docs`, `/peru-api/docs`).

## Archivos relacionados en este repo
- `nginx/evaluaciones-ip.conf`
- `nginx/project-ops.conf`
