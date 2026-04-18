#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-164.68.118.86}"

ok=0
warn=0
fail=0

print_ok() {
  echo "[OK] $1"
  ok=$((ok + 1))
}

print_warn() {
  echo "[WARN] $1"
  warn=$((warn + 1))
}

print_fail() {
  echo "[FAIL] $1"
  fail=$((fail + 1))
}

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    print_ok "Comando disponible: $cmd"
  else
    print_fail "Comando faltante: $cmd"
  fi
}

check_http() {
  local url="$1"
  local name="$2"
  local code

  code="$(curl -sS -o /dev/null -w "%{http_code}" "$url" || echo 000)"
  if [[ "$code" =~ ^[0-9]{3}$ ]] && [ "$code" -ge 200 ] && [ "$code" -lt 400 ]; then
    print_ok "$name -> $url (HTTP $code)"
  else
    print_fail "$name -> $url (HTTP $code)"
  fi
}

check_container() {
  local name="$1"
  if docker ps --format '{{.Names}}' | grep -qx "$name"; then
    print_ok "Contenedor activo: $name"
  else
    print_fail "Contenedor no activo: $name"
  fi
}

echo "=== Project Ops | Post-Deploy Check ==="
echo "Host objetivo: $HOST"
echo

echo "-- 1) Dependencias --"
check_cmd nginx
check_cmd systemctl
check_cmd docker
check_cmd curl
echo

echo "-- 2) Estado de nginx --"
if nginx -t >/tmp/project_ops_nginx_test.log 2>&1; then
  print_ok "nginx -t valido"
else
  print_fail "nginx -t con errores (ver /tmp/project_ops_nginx_test.log)"
fi

if systemctl is-active --quiet nginx; then
  print_ok "nginx activo"
else
  print_fail "nginx inactivo"
fi
echo

echo "-- 3) Contenedores criticos --"
check_container project_ops_app
check_container project_ops_api
check_container project_ops_app_peru
check_container project_ops_api_peru
check_container project_ops_mysql
check_container project_ops_mysql_peru
echo

echo "-- 4) Endpoints publicos --"
check_http "http://$HOST/colombia/" "Dashboard Colombia"
check_http "http://$HOST/peru/" "Dashboard Peru"
check_http "http://$HOST/colombia-api/docs" "API Colombia Docs"
check_http "http://$HOST/peru-api/docs" "API Peru Docs"
echo

echo "-- 5) Chequeo rapido de conflictos nginx --"
conflicts="$(nginx -t 2>&1 | grep -ci 'conflicting server name' || true)"
if [ "$conflicts" -gt 0 ]; then
  print_warn "Se detectaron $conflicts warnings de 'conflicting server name'"
else
  print_ok "Sin warnings de 'conflicting server name'"
fi

echo
echo "=== Resumen ==="
echo "OK:    $ok"
echo "WARN:  $warn"
echo "FAIL:  $fail"

if [ "$fail" -gt 0 ]; then
  exit 1
fi

exit 0