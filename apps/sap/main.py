# apps/sap/main.py
import streamlit as st
import pandas as pd
import csv
import io
from datetime import date
from domain.services import sap_service


MES_ORDER = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def render():
    st.markdown("""
    <style>
    .block-container { max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title("SAP Report")

    # ── Tabs ──
    tab_ver, tab_cargar, tab_gsheets = st.tabs(["📊 Ver Reporte", "📁 Cargar CSV", "🔗 Google Sheets"])

    # ===================== TAB VER =====================
    with tab_ver:
        _render_view()

    # ===================== TAB CARGAR CSV =====================
    with tab_cargar:
        _render_csv_upload()

    # ===================== TAB GOOGLE SHEETS =====================
    with tab_gsheets:
        _render_gsheets()


def _render_view():
    anios = sap_service.get_anios()
    if not anios:
        st.info("No hay datos SAP cargados. Usa las pestañas 'Cargar CSV' o 'Google Sheets' para importar datos.")
        return

    cur_year = date.today().year
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sel_anio = st.selectbox("AÑO", anios, index=anios.index(cur_year) if cur_year in anios else 0, key="sap_anio")
    with fc2:
        meses_disp = sap_service.get_meses(sel_anio)
        sel_mes = st.multiselect("MES", meses_disp, default=[], key="sap_mes")
    with fc3:
        proys = sap_service.get_proyectos_sap(sel_anio)
        proy_opts = [f"{p['id_sap']} - {p['proyecto_sap']}" for p in proys]
        sel_proy = st.multiselect("PROYECTO SAP", proy_opts, default=[], key="sap_proy")
    with fc4:
        search = st.text_input("Buscar colaborador", key="sap_search")

    # Obtener datos
    items = sap_service.listar(anio=sel_anio)
    if not items:
        st.info("Sin datos para el año seleccionado.")
        return

    df = pd.DataFrame([i.model_dump() for i in items])

    # Filtros
    if sel_mes:
        df = df[df["mes"].isin(sel_mes)]
    if sel_proy:
        ids_sel = [p.split(" - ")[0].strip() for p in sel_proy]
        df = df[df["id_sap"].isin(ids_sel)]
    if search:
        df = df[df["colaborador"].str.contains(search, case=False, na=False)]

    # Ordenar meses
    df["mes_ord"] = df["mes"].map({m: i for i, m in enumerate(MES_ORDER)})
    df = df.sort_values(["mes_ord", "id_sap", "colaborador"]).drop(columns=["mes_ord"])

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total registros", len(df))
    k2.metric("Colaboradores únicos", df["colaborador"].nunique())
    k3.metric("Proyectos SAP", df["id_sap"].nunique())
    k4.metric("Total horas", f"{df['horas_mes'].sum():,.0f}")

    # Tabla
    disp = df[["nro", "id_empleado_sap", "colaborador", "id_sap", "proyecto_sap",
               "horas_mes", "mes", "tipo_novedad", "tiempo_novedad_hrs", "reporte_sap"]].copy()
    disp.columns = ["NRO", "ID EMPLEADO SAP", "COLABORADOR", "ID SAP", "PROYECTO SAP",
                     "HORAS MES", "MES", "TIPO NOVEDAD", "TIEMPO NOVEDAD (HRS)", "REPORTE SAP"]

    st.dataframe(disp, use_container_width=True, hide_index=True, height=600)

    # Resumen por proyecto
    st.markdown("---")
    st.markdown("#### Resumen por Proyecto SAP")
    if not df.empty:
        resumen = df.groupby(["id_sap", "proyecto_sap"]).agg(
            colaboradores=("colaborador", "nunique"),
            total_horas=("horas_mes", "sum"),
            reportados=("reporte_sap", "sum"),
        ).reset_index()
        resumen.columns = ["ID SAP", "PROYECTO SAP", "COLABORADORES", "TOTAL HORAS", "REPORTADOS SAP"]
        st.dataframe(resumen, use_container_width=True, hide_index=True)


def _render_csv_upload():
    st.markdown("#### Cargar datos desde archivo CSV")
    st.markdown("El CSV debe tener las columnas: `NRO`, `ID EMPLEADO SAP`, `COLABORADORES`, `ID SAP`, `PROYECTO SAP`, `HORAS MES`, `MES`, `TIPO NOVEDAD`, `TIEMPO NOVEDAD (HRS)`, `REPORTE SAP`")

    col1, col2 = st.columns(2)
    with col1:
        anio = st.number_input("Año", min_value=2020, max_value=2100, value=date.today().year, key="csv_anio")
    with col2:
        modo = st.selectbox("Modo", ["Agregar/Actualizar", "Reemplazar todo del año"], key="csv_modo")

    uploaded = st.file_uploader("Seleccionar CSV", type=["csv"], key="csv_upload")

    if uploaded and st.button("Cargar datos", type="primary", key="csv_btn"):
        try:
            content = uploaded.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            csv_rows = list(reader)

            if not csv_rows:
                st.error("El CSV está vacío.")
                return

            parsed = sap_service.parse_csv_rows(csv_rows, anio=anio)

            if modo == "Reemplazar todo del año":
                # Obtener meses únicos de los datos
                meses_unicos = set(r["mes"] for r in parsed)
                for m in meses_unicos:
                    sap_service.eliminar_mes(anio, m)

            count = sap_service.bulk_upsert(parsed)
            st.success(f"✅ {len(parsed)} registros procesados ({count} filas afectadas en BD)")
            st.rerun()
        except Exception as e:
            st.error(f"Error al procesar CSV: {e}")


def _render_gsheets():
    st.markdown("#### Sincronizar desde Google Sheets")
    st.markdown("""
    Para sincronizar automáticamente desde Google Sheets necesitas una **Service Account** de Google Cloud.

    **Pasos para configurar:**
    1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
    2. Crear un proyecto o usar uno existente
    3. Habilitar la **Google Sheets API**
    4. Crear una **Service Account** en IAM → Cuentas de servicio
    5. Descargar el archivo JSON de credenciales
    6. Compartir el Google Sheet con el email de la Service Account (como Lector)
    7. Subir el JSON aquí abajo
    """)

    # Check if credentials are already configured
    import os
    cred_path = os.path.join(os.path.dirname(__file__), "..", "..", "google_credentials.json")
    cred_exists = os.path.exists(cred_path)

    if cred_exists:
        st.success("✅ Credenciales de Service Account configuradas")

        sheet_url = st.text_input(
            "URL del Google Sheet",
            value="https://docs.google.com/spreadsheets/d/1AVAbgKqo0AcVr97hoA_IQdzFmQW3ZVvmyZvRhwmxsXA/edit",
            key="gsheet_url"
        )
        gid = st.text_input("GID de la hoja", value="1343639467", key="gsheet_gid")
        anio = st.number_input("Año", min_value=2020, max_value=2100, value=date.today().year, key="gs_anio")

        if st.button("🔄 Sincronizar ahora", type="primary", key="gs_sync"):
            try:
                rows = _fetch_google_sheet(cred_path, sheet_url, gid)
                if rows:
                    parsed = sap_service.parse_csv_rows(rows, anio=anio)
                    # Eliminar meses existentes y recargar
                    meses_unicos = set(r["mes"] for r in parsed)
                    for m in meses_unicos:
                        sap_service.eliminar_mes(anio, m)
                    count = sap_service.bulk_upsert(parsed)
                    st.success(f"✅ {len(parsed)} registros sincronizados desde Google Sheets ({count} filas)")
                    st.rerun()
                else:
                    st.warning("No se obtuvieron datos del Sheet.")
            except Exception as e:
                st.error(f"Error al sincronizar: {e}")
    else:
        st.warning("⚠️ No hay credenciales configuradas.")
        uploaded_cred = st.file_uploader("Subir JSON de Service Account", type=["json"], key="gs_cred")
        if uploaded_cred and st.button("Guardar credenciales", key="gs_save"):
            with open(cred_path, "wb") as f:
                f.write(uploaded_cred.read())
            st.success("✅ Credenciales guardadas correctamente.")
            st.rerun()

    st.markdown("---")
    st.markdown("**Alternativa:** También puedes cargar datos usando la pestaña **Cargar CSV** exportando el Sheet como CSV.")


def _fetch_google_sheet(cred_path: str, sheet_url: str, gid: str) -> list:
    """Obtiene datos de Google Sheet usando Service Account."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        st.error("Faltan dependencias. Ejecuta: `pip install gspread google-auth`")
        return []

    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(cred_path, scopes=scopes)
    gc = gspread.authorize(creds)

    # Extraer spreadsheet ID de la URL
    import re
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not match:
        st.error("URL de Google Sheet inválida")
        return []

    spreadsheet_id = match.group(1)
    sh = gc.open_by_key(spreadsheet_id)

    # Buscar la hoja por GID
    worksheet = None
    for ws in sh.worksheets():
        if str(ws.id) == str(gid):
            worksheet = ws
            break

    if not worksheet:
        worksheet = sh.sheet1  # fallback a primera hoja

    records = worksheet.get_all_records()
    return records
