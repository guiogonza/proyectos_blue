# apps/dashboard_financiero/main.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from infra.db.connection import get_conn
from shared.auth.auth import is_admin, get_user_proyectos


# ─── Queries ────────────────────────────────────────────────────────────────
def _fetch_df(sql, params=None):
    """Ejecuta SQL y devuelve un DataFrame usando DictCursor (pymysql)."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params or ())
        rows = cur.fetchall()
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _query_proyectos():
    return _fetch_df("""
        SELECT pr.id, pr.NOMBRE, pr.cliente, pr.PAIS, pr.BUDGET, pr.ESTADO,
               pr.FECHA_INICIO, pr.FECHA_FIN_ESTIMADA, pr.COSTO_REAL_TOTAL
        FROM proyectos pr
        ORDER BY pr.NOMBRE
    """)


def _query_anexos():
    return _fetch_df("""
        SELECT d.id, d.proyecto_id, pr.NOMBRE AS proyecto, pr.cliente, pr.PAIS,
               d.valor, d.iva, d.fecha_documento
        FROM documentos d
        JOIN proyectos pr ON pr.id = d.proyecto_id
        WHERE d.valor IS NOT NULL AND d.valor > 0
        ORDER BY d.fecha_documento
    """)


def _query_colaboradores():
    return _fetch_df("""
        SELECT a.id, a.persona_id, per.nombre AS colaborador,
               per.ROL_PRINCIPAL AS categoria, per.SENIORITY AS seniority,
               a.proyecto_id, pr.NOMBRE AS proyecto, pr.cliente, pr.PAIS,
               a.dedicacion_horas, a.tarifa, per.COSTO_RECURSO,
               a.fecha_asignacion, a.fecha_fin
        FROM asignaciones a
        JOIN personas per ON per.id = a.persona_id
        JOIN proyectos pr ON pr.id = a.proyecto_id
        ORDER BY a.fecha_asignacion, pr.NOMBRE, per.nombre
    """)


# ─── Helpers ────────────────────────────────────────────────────────────────
def _quarter(d):
    if isinstance(d, str):
        d = pd.to_datetime(d)
    return (d.month - 1) // 3 + 1


def _expand_months(df_colab, year):
    """Expande asignaciones a filas por mes dentro del año."""
    rows = []
    for _, r in df_colab.iterrows():
        fi = r["fecha_asignacion"]
        ff = r["fecha_fin"] if pd.notna(r["fecha_fin"]) else date(year, 12, 31)
        if hasattr(fi, 'date') and callable(fi.date):
            fi = fi.date()
        if hasattr(ff, 'date') and callable(ff.date):
            ff = ff.date()

        start_m = max(fi.month, 1) if fi.year == year else (1 if fi.year < year else 13)
        end_m = min(ff.month, 12) if ff.year == year else (12 if ff.year > year else 0)
        if fi.year < year:
            start_m = 1
        if ff.year > year:
            end_m = 12

        for m in range(start_m, end_m + 1):
            tarifa = float(r["tarifa"]) if pd.notna(r["tarifa"]) and float(r["tarifa"]) > 0 else 0
            costo_recurso = float(r["COSTO_RECURSO"]) if pd.notna(r["COSTO_RECURSO"]) else 0
            horas = float(r["dedicacion_horas"])
            costo_mes = costo_recurso * horas
            factura_mes = tarifa * horas
            q = (m - 1) // 3 + 1
            rows.append({
                "mes": m,
                "trimestre": q,
                "proyecto_id": r["proyecto_id"],
                "proyecto": r["proyecto"],
                "cliente": r.get("cliente", ""),
                "pais": r.get("PAIS", ""),
                "colaborador": r["colaborador"],
                "categoria": r["categoria"],
                "seniority": r["seniority"] if pd.notna(r.get("seniority")) else "",
                "horas": horas,
                "tarifa": tarifa,
                "costo_recurso": costo_recurso,
                "costo_mes": costo_mes,
                "factura_mes": factura_mes,
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _fmt(val):
    """Formatea número como moneda con puntos de miles."""
    if val < 0:
        return f"$ -{abs(val):,.0f}".replace(",", ".")
    return f"$ {val:,.0f}".replace(",", ".")


# ─── Plotly dark theme ──────────────────────────────────────────────────────
_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#cdd6f4", size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=60, r=60, t=40, b=40),
)
_GRID = dict(gridcolor="#313244", zerolinecolor="#313244")


# ─── Render ─────────────────────────────────────────────────────────────────
def render():
    st.markdown("""
    <style>
    /* Ampliar el contenedor principal */
    .block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    .kpi-card {
        background: linear-gradient(135deg, #1e1e2e, #2a2a3e);
        border: 1px solid #313244;
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        height: 100%;
    }
    .kpi-label { color: #a6adc8; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; white-space: nowrap; }
    .kpi-value { color: #cdd6f4; font-size: 20px; font-weight: 700; white-space: nowrap; }
    .kpi-green { color: #a6e3a1; font-size: 28px; font-weight: 700; white-space: nowrap; }
    </style>
    """, unsafe_allow_html=True)

    st.title("Proyectos")

    # ── Cargar datos ──
    df_proy = _query_proyectos()
    df_anexos = _query_anexos()
    df_colab_raw = _query_colaboradores()

    # Convertir columnas numéricas (pymysql puede devolver strings)
    df_proy["BUDGET"] = pd.to_numeric(df_proy["BUDGET"], errors="coerce").fillna(0)
    df_proy["FECHA_INICIO"] = pd.to_datetime(df_proy["FECHA_INICIO"], errors="coerce")
    if not df_anexos.empty:
        df_anexos["valor"] = pd.to_numeric(df_anexos["valor"], errors="coerce").fillna(0)
        df_anexos["iva"] = pd.to_numeric(df_anexos["iva"], errors="coerce").fillna(0)
        df_anexos["fecha_documento"] = pd.to_datetime(df_anexos["fecha_documento"], errors="coerce")
    if not df_colab_raw.empty:
        df_colab_raw["dedicacion_horas"] = pd.to_numeric(df_colab_raw["dedicacion_horas"], errors="coerce").fillna(0)
        df_colab_raw["tarifa"] = pd.to_numeric(df_colab_raw["tarifa"], errors="coerce").fillna(0)
        df_colab_raw["COSTO_RECURSO"] = pd.to_numeric(df_colab_raw["COSTO_RECURSO"], errors="coerce").fillna(0)
        df_colab_raw["fecha_asignacion"] = pd.to_datetime(df_colab_raw["fecha_asignacion"], errors="coerce")
        df_colab_raw["fecha_fin"] = pd.to_datetime(df_colab_raw["fecha_fin"], errors="coerce")

    if not is_admin():
        pp = get_user_proyectos()
        if pp:
            df_proy = df_proy[df_proy["id"].isin(pp)]
            df_anexos = df_anexos[df_anexos["proyecto_id"].isin(pp)]
            df_colab_raw = df_colab_raw[df_colab_raw["proyecto_id"].isin(pp)]

    # ── Filtros ──
    fc1, fc2, fc3, fc4, fc5 = st.columns([1, 1, 1, 0.7, 0.7])
    with fc1:
        sel_proy = st.multiselect("PROYECTO", sorted(df_proy["NOMBRE"].unique()), default=[], key="df_proy")
    with fc2:
        sel_cli = st.multiselect("CLIENTE", sorted(df_proy["cliente"].dropna().unique()), default=[], key="df_cli")
    with fc3:
        sel_pais = st.multiselect("PAIS", sorted(df_proy["PAIS"].dropna().unique()), default=[], key="df_pais")
    cur_year = date.today().year
    with fc4:
        fecha_inicio = st.date_input("DESDE", value=date(cur_year, 1, 1), key="df_desde")
    with fc5:
        fecha_fin = st.date_input("HASTA", value=date(cur_year, 12, 31), key="df_hasta")
    sel_year = fecha_inicio.year

    # ── Filtrar ──
    df_f = df_proy.copy()
    if sel_proy:
        df_f = df_f[df_f["NOMBRE"].isin(sel_proy)]
    if sel_cli:
        df_f = df_f[df_f["cliente"].isin(sel_cli)]
    if sel_pais:
        df_f = df_f[df_f["PAIS"].isin(sel_pais)]

    # Filtrar proyectos cuyo rango de fechas intersecte con el periodo seleccionado
    fi_ts = pd.Timestamp(fecha_inicio)
    ff_ts = pd.Timestamp(fecha_fin)
    df_f["FECHA_INICIO"] = pd.to_datetime(df_f["FECHA_INICIO"], errors="coerce")
    df_f["FECHA_FIN_ESTIMADA"] = pd.to_datetime(df_f["FECHA_FIN_ESTIMADA"], errors="coerce")
    df_f = df_f[
        (df_f["FECHA_INICIO"] <= ff_ts) &
        (df_f["FECHA_FIN_ESTIMADA"].fillna(pd.Timestamp("2099-12-31")) >= fi_ts)
    ]

    pids = set(df_f["id"].tolist())
    df_anx = df_anexos[df_anexos["proyecto_id"].isin(pids)].copy()
    df_col = df_colab_raw[df_colab_raw["proyecto_id"].isin(pids)].copy()

    # Filtrar colaboradores por rango de fechas (asignaciones que intersectan el rango)
    if not df_col.empty:
        df_col = df_col[
            (df_col["fecha_asignacion"] <= ff_ts) &
            (df_col["fecha_fin"].fillna(pd.Timestamp("2099-12-31")) >= fi_ts)
        ]

    # Expandir a meses
    df_exp = _expand_months(df_col, sel_year)

    # ── KPIs ──
    budget = float(df_f["BUDGET"].fillna(0).sum())
    facturar = float(df_anx["valor"].sum()) if not df_anx.empty else 0
    costo = float(df_exp["costo_mes"].sum()) if not df_exp.empty else 0
    gross = facturar - costo
    margen = (gross / facturar * 100) if facturar > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f'<div class="kpi-card"><div class="kpi-label">BUDGET</div><div class="kpi-value">{_fmt(budget)}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="kpi-card"><div class="kpi-label">MONTO A FACTURAR</div><div class="kpi-value">{_fmt(facturar)}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="kpi-card"><div class="kpi-label">COSTO</div><div class="kpi-value">{_fmt(costo)}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="kpi-card"><div class="kpi-label">GROSS</div><div class="kpi-value">{_fmt(gross)}</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="kpi-card"><div class="kpi-label">MARGEN</div><div class="kpi-green">{margen:.0f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gráfico: Facturación, Costo y Margen por Q ──
    st.markdown("#### FACTURACIÓN, COSTO Y MARGEN POR Q")

    qs = [1, 2, 3, 4]
    ql = ["1", "2", "3", "4"]

    fq = {q: 0.0 for q in qs}
    cq = {q: 0.0 for q in qs}
    aq = {q: 0.0 for q in qs}
    mq = {q: 0.0 for q in qs}

    if not df_anx.empty:
        df_anx["q"] = pd.to_datetime(df_anx["fecha_documento"]).apply(_quarter)
        for q in qs:
            fq[q] = float(df_anx[df_anx["q"] == q]["valor"].sum())
            aq[q] = float(df_anx[df_anx["q"] == q]["iva"].sum())

    if not df_exp.empty:
        for q in qs:
            cq[q] = float(df_exp[df_exp["trimestre"] == q]["costo_mes"].sum())

    for q in qs:
        mq[q] = (fq[q] - cq[q]) / fq[q] if fq[q] > 0 else 0

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=ql, y=[fq[q] for q in qs], name="MONTO A FACTURAR",
                              line=dict(color="#4FC3F7", width=2.5)))
    fig1.add_trace(go.Scatter(x=ql, y=[cq[q] for q in qs], name="COSTO",
                              line=dict(color="#FFB74D", width=2.5)))
    fig1.add_trace(go.Scatter(x=ql, y=[aq[q] for q in qs], name="ANEXO",
                              line=dict(color="#BA68C8", width=2.5)))
    fig1.add_trace(go.Scatter(x=ql, y=[mq[q] for q in qs], name="MARGEN",
                              line=dict(color="#a6e3a1", width=2.5), yaxis="y2"))
    fig1.update_layout(
        **_DARK,
        xaxis=dict(**_GRID),
        yaxis=dict(title="MONTO A FACTURAR | COSTO | MARGEN", **_GRID),
        yaxis2=dict(title="ANEXO", overlaying="y", side="right", gridcolor="#313244",
                    range=[-0.1, 1.1], tickformat=".0%"),
        height=370,
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ── Top Proyectos Margen + Por Ejecutar ──
    gc1, gc2 = st.columns(2)

    with gc1:
        st.markdown("#### TOP PROYECTOS MARGEN")
        if not df_exp.empty:
            pc = df_exp.groupby("proyecto")["costo_mes"].sum().reset_index()
            pc.columns = ["proyecto", "costo"]
        else:
            pc = pd.DataFrame(columns=["proyecto", "costo"])

        if not df_anx.empty:
            pf = df_anx.groupby("proyecto")["valor"].sum().reset_index()
            pf.columns = ["proyecto", "factura"]
        else:
            pf = pd.DataFrame(columns=["proyecto", "factura"])

        if not pf.empty:
            pm = pf.merge(pc, on="proyecto", how="left").fillna(0)
            pm["margen_pct"] = ((pm["factura"] - pm["costo"]) / pm["factura"] * 100).clip(0, 100)
            pm = pm.sort_values("margen_pct", ascending=True).tail(10)

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                y=pm["proyecto"], x=pm["margen_pct"], orientation="h",
                marker_color="#4FC3F7",
                text=[f"{v:.0f} %" for v in pm["margen_pct"]],
                textposition="outside",
            ))
            fig2.update_layout(**_DARK, height=370, xaxis=dict(range=[0, 115], title="", **_GRID),
                               yaxis=dict(title="", **_GRID), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sin datos de facturación.")

    with gc2:
        st.markdown("#### POR EJECUTAR")
        pe = {}
        acum = 0
        for q in qs:
            acum += fq[q]
            pe[q] = max(budget - acum, 0)

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ql, y=[pe[q] for q in qs], name="POR EJECUTAR",
                                  line=dict(color="#4FC3F7", width=2.5)))
        fig3.update_layout(**_DARK, height=370,
                           xaxis=dict(**_GRID),
                           yaxis=dict(title="POR EJECUTAR", **_GRID),
                           showlegend=True)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Tabla COLABORADORES ──
    st.markdown("#### COLABORADORES")

    if not df_exp.empty:
        tf1, tf2, tf3 = st.columns(3)
        meses_map = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
                     7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
        with tf1:
            sel_mes = st.multiselect("MES", sorted(df_exp["mes"].unique()), default=[],
                                     format_func=lambda x: meses_map.get(x, x), key="dt_mes")
        with tf2:
            sel_pt = st.multiselect("PROYECTO", sorted(df_exp["proyecto"].unique()), default=[], key="dt_proy")
        with tf3:
            sel_cb = st.multiselect("COLABORADOR", sorted(df_exp["colaborador"].unique()), default=[], key="dt_col")

        dt = df_exp.copy()
        if sel_mes:
            dt = dt[dt["mes"].isin(sel_mes)]
        if sel_pt:
            dt = dt[dt["proyecto"].isin(sel_pt)]
        if sel_cb:
            dt = dt[dt["colaborador"].isin(sel_cb)]

        dt["periodo"] = dt["trimestre"]
        disp = dt[["periodo", "mes", "proyecto", "colaborador", "categoria", "seniority", "horas", "tarifa"]].copy()
        disp.columns = ["PERIODO", "MES", "PROYECTO", "COLABORADOR", "CATEGORÍA", "SENIORITY", "HORAS LABORADAS", "TARIFA"]
        disp = disp.sort_values(["PERIODO", "MES", "PROYECTO", "COLABORADOR"])
        disp["TARIFA"] = disp["TARIFA"].apply(lambda x: f"$ {x:,.2f}".replace(",", ".") if x > 0 else "$ 0,00")

        st.dataframe(disp, use_container_width=True, hide_index=True, height=500)
        st.caption(f"Total registros: {len(disp)}")
    else:
        st.info("No hay asignaciones para el periodo seleccionado.")
