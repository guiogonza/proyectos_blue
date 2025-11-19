# apps/proyectos/main.py
import streamlit as st
from datetime import date
from domain.schemas.proyectos import ProyectoCreate, ProyectoUpdate, ProyectoClose, ESTADOS_PROY
from domain.services import proyectos_service
from shared.utils.exports import export_csv

def _header_resumen(items):
    tot = len(items)
    activos = sum(1 for x in items if x.estado == "Activo")
    cerrados = sum(1 for x in items if x.estado == "Cerrado")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", tot)
    col2.metric("Activos", activos)
    col3.metric("Cerrados", cerrados)

def render():
    st.title("📁 Gestión de Proyectos")

    # ----- Filtros -----
    colf1, colf2, colf3 = st.columns([1,1,2])
    with colf1:
        estado = st.selectbox("Estado", options=["(Todos)"] + ESTADOS_PROY, index=0)
        estado_val = None if estado == "(Todos)" else estado
    with colf2:
        clientes = proyectos_service.clientes()
        cliente = st.selectbox("Cliente", options=["(Todos)"] + clientes, index=0) if clientes else "(Todos)"
        cliente_val = None if cliente == "(Todos)" else cliente
    with colf3:
        search = st.text_input("Buscar por nombre/cliente", "")

    items = proyectos_service.listar(estado_val, cliente_val, (search or None))
    _header_resumen(items)

    # Export
    if st.button("📤 Exportar CSV"):
        path = export_csv([i.dict() for i in items], "proyectos")
        st.toast(f"Exportado a {path}", icon="✅")

    # Tabla
    if items:
        st.dataframe([i.dict() for i in items], use_container_width=True, hide_index=True)
    else:
        st.info("No hay proyectos con ese filtro.")

    st.markdown("---")
    st.subheader("➕ Crear / ✏️ Editar / ✅ Cerrar / 🗑️ Eliminar")

    tab_create, tab_edit, tab_close, tab_delete = st.tabs(["Crear", "Editar", "Cerrar", "Eliminar"])

    # ---- Crear ----
    with tab_create:
        with st.form("form_create_proj", clear_on_submit=True):
            col1, col2 = st.columns([2,2])
            nombre = col1.text_input("Nombre", "")
            cliente = col2.text_input("Cliente (opcional)", "")
            col3, col4, col5 = st.columns([1,1,1])
            fi = col3.date_input("Inicio", value=date.today())
            ff = col4.date_input("Fin planeada", value=date.today())
            estado_c = col5.selectbox("Estado", options=ESTADOS_PROY, index=0)
            costo_est = st.number_input("Costo estimado total", min_value=0.0, value=0.0, step=100000.0, format="%.2f")
            pms = proyectos_service.pms_activos()
            pm_label = st.selectbox("PM (opcional)", ["(Sin PM)"] + [f"{pid} - {name}" for pid, name in pms.items()])
            pm_id = None if pm_label == "(Sin PM)" else int(pm_label.split(" - ")[0])
            if st.form_submit_button("Crear"):
                try:
                    dto = ProyectoCreate(
                        nombre=nombre.strip(),
                        cliente=(cliente.strip() or None),
                        pm_id=pm_id,
                        fecha_inicio=fi,
                        fecha_fin_planeada=ff,
                        estado=estado_c,
                        costo_estimado_total=costo_est,
                    )
                    pid = proyectos_service.crear(dto)
                    st.success(f"Proyecto creado ID {pid}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ---- Editar ----
    with tab_edit:
        options = {f"{i.id} - {i.nombre} ({i.estado})": i for i in items}
        if not options:
            st.info("No hay proyectos para editar con el filtro actual.")
        else:
            sel_key = st.selectbox("Selecciona proyecto", list(options.keys()))
            sel = options[sel_key]
            with st.form("form_edit_proj"):
                col1, col2 = st.columns([2,2])
                nombre_e = col1.text_input("Nombre", sel.nombre)
                cliente_e = col2.text_input("Cliente", sel.cliente or "")
                col3, col4, col5 = st.columns([1,1,1])
                fi_e = col3.date_input("Inicio", value=sel.fecha_inicio)
                ff_e = col4.date_input("Fin planeada", value=sel.fecha_fin_planeada)
                estado_e = col5.selectbox("Estado", options=ESTADOS_PROY, index=ESTADOS_PROY.index(sel.estado))
                costo_e = st.number_input("Costo estimado total", min_value=0.0, value=float(sel.costo_estimado_total), step=100000.0, format="%.2f")
                pms = proyectos_service.pms_activos()
                pm_label_e = st.selectbox("PM (opcional)", ["(Sin PM)"] + [f"{pid} - {name}" for pid, name in pms.items()], index=0)
                pm_id_e = None if pm_label_e == "(Sin PM)" else int(pm_label_e.split(" - ")[0])
                if st.form_submit_button("Guardar cambios"):
                    try:
                        dto = ProyectoUpdate(
                            id=sel.id,
                            nombre=nombre_e.strip(),
                            cliente=(cliente_e.strip() or None),
                            pm_id=pm_id_e,
                            fecha_inicio=fi_e,
                            fecha_fin_planeada=ff_e,
                            estado=estado_e,
                            costo_estimado_total=costo_e,
                        )
                        proyectos_service.actualizar(dto)
                        st.success("Cambios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # ---- Cerrar ----
    with tab_close:
        options2 = {f"{i.id} - {i.nombre} ({i.estado})": i for i in items if i.estado != "Cerrado"}
        if not options2:
            st.info("No hay proyectos abiertos para cerrar.")
        else:
            sel_key2 = st.selectbox("Selecciona proyecto a cerrar", list(options2.keys()))
            sel2 = options2[sel_key2]
            costo_real = st.number_input("Costo real total", min_value=0.0, value=float(sel2.costo_estimated_total if hasattr(sel2, 'costo_estimated_total') else sel2.costo_estimado_total), step=100000.0, format="%.2f")
            if st.button("Cerrar proyecto"):
                try:
                    dto = ProyectoClose(id=sel2.id, costo_real_total=costo_real)
                    proyectos_service.cerrar(dto)
                    st.success("Proyecto cerrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ---- Eliminar ----
    with tab_delete:
        st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el proyecto y todos sus sprints y asignaciones asociadas.")
        options_del = {f"{i.id} - {i.nombre} ({i.estado})": i for i in items}
        if not options_del:
            st.info("No hay proyectos para eliminar con el filtro actual.")
        else:
            sel_del = options_del[st.selectbox("Selecciona proyecto a eliminar", list(options_del.keys()), key="delete_select_proyecto")]
            st.error(f"Vas a eliminar: **{sel_del.nombre}** (ID: {sel_del.id})")
            confirmar = st.checkbox("Confirmo que deseo eliminar este proyecto", key="confirm_delete_proyecto")
            if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                try:
                    proyectos_service.eliminar(sel_del.id)
                    st.success(f"Proyecto '{sel_del.nombre}' eliminado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {str(e)}")
