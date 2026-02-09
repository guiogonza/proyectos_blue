# apps/mapa_recursos/main.py
import streamlit as st
import calendar
from datetime import date
from collections import defaultdict
from infra.db.connection import get_conn
from shared.auth.auth import is_admin, get_user_proyectos

# Paleta de colores distinguibles para proyectos
_COLORS = [
    "#4FC3F7", "#81C784", "#FFB74D", "#E57373", "#BA68C8",
    "#4DD0E1", "#AED581", "#FFD54F", "#FF8A65", "#F06292",
    "#7986CB", "#A1887F", "#90A4AE", "#DCE775", "#4DB6AC",
    "#FFF176", "#CE93D8", "#80DEEA", "#C5E1A5", "#FFAB91",
]

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def _get_all_assignments(year: int):
    """Obtiene todas las asignaciones que intersectan con el año dado."""
    sql = """
        SELECT a.id, a.persona_id, p.nombre AS persona, p.ROL_PRINCIPAL AS rol,
               a.proyecto_id, pr.nombre AS proyecto, a.dedicacion_horas,
               a.fecha_asignacion, a.fecha_fin
        FROM asignaciones a
        JOIN personas p ON p.id = a.persona_id
        JOIN proyectos pr ON pr.id = a.proyecto_id
        WHERE a.fecha_asignacion <= %s
          AND (a.fecha_fin IS NULL OR a.fecha_fin >= %s)
          AND p.activo = 1
        ORDER BY p.nombre, a.fecha_asignacion
    """
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (year_end, year_start))
        return cur.fetchall()


def _build_matrix(rows, year):
    """
    Construye un dict:
      persona_key -> {
        'nombre': str, 'rol': str, 'persona_id': int,
        'meses': { 1..12: [ { 'proyecto': str, 'horas': float, 'proyecto_id': int } ] }
      }
    """
    matrix = {}
    for r in rows:
        pid = r["persona_id"]
        if pid not in matrix:
            matrix[pid] = {
                "nombre": r["persona"],
                "rol": r["rol"] or "",
                "persona_id": pid,
                "meses": {m: [] for m in range(1, 13)},
            }

        fi = r["fecha_asignacion"]
        ff = r["fecha_fin"] or date(year, 12, 31)

        # Clamp al año
        start_m = max(fi.month, 1) if fi.year == year else (1 if fi.year < year else 13)
        end_m = min(ff.month, 12) if ff.year == year else (12 if ff.year > year else 0)

        if fi.year < year:
            start_m = 1
        if ff.year > year:
            end_m = 12

        for m in range(start_m, end_m + 1):
            matrix[pid]["meses"][m].append({
                "proyecto": r["proyecto"],
                "horas": float(r["dedicacion_horas"]),
                "proyecto_id": r["proyecto_id"],
            })

    return matrix


def _assign_colors(matrix):
    """Asigna un color único a cada proyecto."""
    all_projects = set()
    for pdata in matrix.values():
        for m in range(1, 13):
            for entry in pdata["meses"][m]:
                all_projects.add(entry["proyecto"])
    sorted_projects = sorted(all_projects)
    color_map = {}
    for i, proj in enumerate(sorted_projects):
        color_map[proj] = _COLORS[i % len(_COLORS)]
    return color_map


def _render_bubble(entries, color_map):
    """Genera HTML para un globo de mes."""
    if not entries:
        return '<div class="bubble bubble-empty">&nbsp;</div>'

    total = sum(e["horas"] for e in entries)

    if len(entries) == 1:
        e = entries[0]
        c = color_map.get(e["proyecto"], "#666")
        return (
            f'<div class="bubble" style="background:{c};" '
            f'title="{e["proyecto"]}: {e["horas"]:.0f}h">'
            f'{e["horas"]:.0f}h</div>'
        )

    # Múltiples proyectos: globo dividido
    segments = []
    for e in entries:
        c = color_map.get(e["proyecto"], "#666")
        pct = (e["horas"] / total * 100) if total > 0 else 0
        segments.append(
            f'<div class="seg" style="background:{c};flex:{e["horas"]};" '
            f'title="{e["proyecto"]}: {e["horas"]:.0f}h">'
            f'{e["horas"]:.0f}</div>'
        )

    return (
        f'<div class="bubble bubble-multi" title="Total: {total:.0f}h">'
        + "".join(segments)
        + '</div>'
    )


def render():
    st.title("📊 Mapa de Recursos")
    st.caption("Asignaciones por persona y mes — pasa el mouse sobre cada globo para ver el detalle.")

    # Selector de año
    current_year = date.today().year
    col_y, col_blank = st.columns([0.3, 0.7])
    with col_y:
        year = st.selectbox("Año", list(range(current_year - 1, current_year + 3)), index=1)

    rows = _get_all_assignments(year)

    # Filtrar por permisos
    if not is_admin():
        proyectos_permitidos = get_user_proyectos()
        if proyectos_permitidos:
            rows = [r for r in rows if r["proyecto_id"] in proyectos_permitidos]

    if not rows:
        st.info("No hay asignaciones para este año.")
        return

    matrix_full = _build_matrix(rows, year)
    color_map_full = _assign_colors(matrix_full)

    # --- Métricas resumen arriba ---
    current_month = date.today().month if year == current_year else 1
    total_personas = len(matrix_full)
    total_proyectos = len(color_map_full)
    under = sum(1 for p in matrix_full.values()
                if 0 < sum(e["horas"] for e in p["meses"][current_month]) < 160)
    sin_asig = sum(1 for p in matrix_full.values()
                   if sum(e["horas"] for e in p["meses"][current_month]) == 0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Personas asignadas", total_personas)
    m2.metric("Proyectos activos", total_proyectos)
    m3.metric(f"Parciales ({MESES_ES[current_month-1]})", under)
    m4.metric(f"Sin asignación ({MESES_ES[current_month-1]})", sin_asig)

    st.markdown("---")

    # --- Filtros persona y proyecto ---
    col_fp, col_fpr = st.columns(2)
    with col_fp:
        personas_list = sorted(set(f"{v['nombre']} ({v['rol']})" for v in matrix_full.values()))
        filtro_persona = st.multiselect("Filtrar personas", personas_list, default=[], key="mapa_filter_persona")
    with col_fpr:
        proyectos_list = sorted(color_map_full.keys())
        filtro_proyecto = st.multiselect("Filtrar proyectos", proyectos_list, default=[], key="mapa_filter_proyecto")

    # Aplicar filtro de persona
    matrix = dict(matrix_full)
    if filtro_persona:
        filtro_nombres = {fp.split(" (")[0] for fp in filtro_persona}
        matrix = {k: v for k, v in matrix.items() if v["nombre"] in filtro_nombres}

    # Aplicar filtro de proyecto: mostrar solo personas que tengan al menos 1 asignación en esos proyectos
    if filtro_proyecto:
        filtered = {}
        for k, v in matrix.items():
            has_project = False
            for m in range(1, 13):
                for e in v["meses"][m]:
                    if e["proyecto"] in filtro_proyecto:
                        has_project = True
                        break
                if has_project:
                    break
            if has_project:
                filtered[k] = v
        matrix = filtered

    color_map = _assign_colors(matrix) if matrix else {}

    # Leyenda de colores
    legend_items = " ".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:14px;">'
        f'<span style="width:14px;height:14px;border-radius:50%;background:{c};display:inline-block;margin-right:4px;"></span>'
        f'<span style="font-size:12px;">{p}</span></span>'
        for p, c in sorted(color_map.items())
    )

    # CSS
    css = """
    <style>
    .rm-table { width:100%; border-collapse:collapse; font-family:'Source Sans Pro',sans-serif; font-size:13px; }
    .rm-table th { background:#1e1e2e; color:#cdd6f4; padding:6px 8px; text-align:center; position:sticky; top:0; z-index:2; font-weight:600; }
    .rm-table td { padding:4px 3px; text-align:center; vertical-align:middle; border-bottom:1px solid #313244; }
    .rm-table td.name-cell { text-align:left; white-space:nowrap; padding-left:8px; font-weight:500; min-width:220px; }
    .rm-table td.rol-cell { text-align:left; white-space:nowrap; color:#a6adc8; font-size:12px; min-width:100px; }
    .rm-table tr:hover { background:#313244; }
    .bubble { display:flex; align-items:center; justify-content:center; min-width:44px; height:34px;
              border-radius:17px; margin:0 auto; font-size:11px; font-weight:700; color:#1e1e2e;
              cursor:default; transition:transform 0.15s; }
    .bubble:hover { transform:scale(1.15); z-index:10; }
    .bubble-empty { background:#45475a; color:#585b70; min-width:44px; font-size:10px; }
    .bubble-multi { padding:0; overflow:hidden; gap:0; }
    .seg { display:flex; align-items:center; justify-content:center; height:100%;
           font-size:10px; font-weight:700; color:#1e1e2e; padding:0 4px; }
    .rm-legend { padding:8px 0 12px 0; line-height:2; }
    .total-ok { color:#a6e3a1; font-weight:700; }
    .total-over { color:#f38ba8; font-weight:700; }
    .total-partial { color:#f9e2af; font-weight:700; }
    </style>
    """

    # Construir tabla HTML
    header = "<tr><th>Persona</th><th>Rol</th>"
    for m in range(1, 13):
        header += f"<th>{MESES_ES[m-1]}</th>"
    header += "<th>Prom</th></tr>"

    body = ""
    sorted_people = sorted(matrix.values(), key=lambda x: x["nombre"])
    for pdata in sorted_people:
        body += f'<tr><td class="name-cell">{pdata["nombre"]}</td>'
        body += f'<td class="rol-cell">{pdata["rol"]}</td>'

        total_h = 0
        active_months = 0
        for m in range(1, 13):
            entries = pdata["meses"][m]
            body += f"<td>{_render_bubble(entries, color_map)}</td>"
            month_total = sum(e["horas"] for e in entries)
            if month_total > 0:
                total_h += month_total
                active_months += 1

        avg = total_h / active_months if active_months > 0 else 0
        if avg == 0:
            cls = ""
        elif avg <= 160:
            cls = "total-ok"
        else:
            cls = "total-over"
        body += f'<td><span class="{cls}">{avg:.0f}h</span></td>'
        body += "</tr>"

    html = f"""
    {css}
    <div class="rm-legend">{legend_items}</div>
    <div style="overflow-x:auto;">
    <table class="rm-table">
    <thead>{header}</thead>
    <tbody>{body}</tbody>
    </table>
    </div>
    """

    if matrix:
        st.html(html)
    else:
        st.info("No hay personas que coincidan con los filtros seleccionados.")
