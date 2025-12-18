import streamlit as st
from datetime import date
from domain.schemas.sprints import SprintCreate, SprintUpdate, SprintClose
from domain.services import sprints_service, proyectos_service
from shared.utils.exports import export_csv
from shared.auth.auth import is_admin, get_user_proyectos

def _proyectos_opts():
    rows = proyectos_service.listar(None, None, None)
    proyectos_permitidos = get_user_proyectos()
    
    options = {}
    for r in rows:
        # Si no es admin, filtrar por proyectos permitidos
        if not is_admin() and proyectos_permitidos and r.id not in proyectos_permitidos:
            continue
        options[f"{r.id} - {r.NOMBRE} ({r.ESTADO})"] = r.id
    return options

def render():
    st.title("🗓️ Sprints por proyecto")

    # Filtros
    pr_opts = _proyectos_opts()
    proyecto_f = st.selectbox("Proyecto (filtro)", ["(Todos)"] + list(pr_opts.keys()))
    proyecto_id = None if proyecto_f == "(Todos)" else pr_opts[proyecto_f]
    estado = st.selectbox("Estado", ["(Todos)","Planificado","En curso","Cerrado"])
    estado_v = None if estado == "(Todos)" else estado
    search = st.text_input("Buscar por nombre")

    items = sprints_service.listar(proyecto_id, estado_v, (search or None))
    
    # Filtrar por proyectos del usuario si no es admin
    if not is_admin():
        proyectos_permitidos = get_user_proyectos()
        if proyectos_permitidos:
            items = [i for i in items if i.proyecto_id in proyectos_permitidos]
    
    st.success(f"{len(items)} sprint(s)")

    if st.button("📤 Exportar CSV"):
        path = export_csv([i.dict() for i in items], "sprints")
        st.toast(f"Exportado a {path}", icon="✅")

    if items:
        st.dataframe([i.dict() for i in items], use_container_width=True, hide_index=True)
    else:
        st.info("No hay sprints con ese filtro.")

    st.markdown("---")
    st.subheader("➡️ Crear / ✏️ Editar / ✅ Cerrar / 🗑️ Eliminar")

    tab_c, tab_e, tab_close, tab_delete = st.tabs(["Crear", "Editar", "Cerrar", "Eliminar"])

    with tab_c:
        with st.form("form_sprint_create", clear_on_submit=True):
            pr_sel = st.selectbox("Proyecto", list(pr_opts.keys()))
            nombre = st.text_input("Nombre", "")
            actividades = st.text_area("Actividades (opcional)", "", height=100, 
                                     help="Describe las actividades o tareas de este sprint")
            c1, c2, c3 = st.columns(3)
            fi = c1.date_input("Inicio", value=date.today())
            ff = c2.date_input("Fin", value=date.today())
            costo = c3.number_input("Costo estimado", min_value=0.0, value=0.0, step=100000.0, format="%.2f")
            estado_c = st.selectbox("Estado", ["Planificado","En curso","Cerrado"], index=0)
            if st.form_submit_button("Crear"):
                try:
                    dto = SprintCreate(proyecto_id=pr_opts[pr_sel], nombre=nombre.strip(),
                                       fecha_inicio=fi, fecha_fin=ff, costo_estimado=costo, estado=estado_c,
                                       actividades=actividades.strip() if actividades.strip() else None)
                    sid = sprints_service.crear(dto)
                    st.success(f"Sprint creado (ID {sid})")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab_e:
        if not items:
            st.info("No hay sprints en el filtro actual.")
        else:
            opt = {f"{i.id} - {i.nombre} ({i.estado})": i for i in items}
            sel_k = st.selectbox("Selecciona sprint", list(opt.keys()))
            sel = opt[sel_k]
            with st.form("form_sprint_edit"):
                pr_sel_e = st.selectbox("Proyecto", list(pr_opts.keys()),
                                        index=list(pr_opts.values()).index(sel.proyecto_id))
                nombre_e = st.text_input("Nombre", sel.nombre)
                actividades_e = st.text_area("Actividades (opcional)", sel.actividades or "", height=100,
                                           help="Describe las actividades o tareas de este sprint")
                c1, c2, c3 = st.columns(3)
                fi_e = c1.date_input("Inicio", value=sel.fecha_inicio)
                ff_e = c2.date_input("Fin", value=sel.fecha_fin)
                costo_e = c3.number_input("Costo estimado", min_value=0.0, value=float(sel.costo_estimado), step=100000.0, format="%.2f")
                estado_e = st.selectbox("Estado", ["Planificado","En curso","Cerrado"], index=["Planificado","En curso","Cerrado"].index(sel.estado))
                if st.form_submit_button("Guardar cambios"):
                    try:
                        dto = SprintUpdate(id=sel.id, proyecto_id=pr_opts[pr_sel_e], nombre=nombre_e.strip(),
                                           fecha_inicio=fi_e, fecha_fin=ff_e, costo_estimado=costo_e, estado=estado_e,
                                           actividades=actividades_e.strip() if actividades_e.strip() else None)
                        sprints_service.actualizar(dto)
                        st.success("Cambios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with tab_close:
        abiertos = [i for i in items if i.estado != "Cerrado"]
        if not abiertos:
            st.info("No hay sprints abiertos.")
        else:
            opt2 = {f"{i.id} - {i.nombre} ({i.estado})": i for i in abiertos}
            sel2_k = st.selectbox("Sprint a cerrar", list(opt2.keys()))
            sel2 = opt2[sel2_k]
            costo_real = st.number_input("Costo real", min_value=0.0, value=float(sel2.costo_estimado), step=100000.0, format="%.2f")
            if st.button("Cerrar sprint"):
                try:
                    dto = SprintClose(id=sel2.id, costo_real=costo_real)
                    sprints_service.cerrar(dto)
                    st.success("Sprint cerrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab_delete:
        st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el sprint y todas sus asignaciones asociadas.")
        if not items:
            st.info("No hay sprints para eliminar con el filtro actual.")
        else:
            opt_del = {f"{i.id} - {i.nombre} ({i.estado})": i for i in items}
            sel_del_k = st.selectbox("Selecciona sprint a eliminar", list(opt_del.keys()), key="delete_select_sprint")
            sel_del = opt_del[sel_del_k]
            st.error(f"Vas a eliminar: **{sel_del.nombre}** (ID: {sel_del.id})")
            confirmar = st.checkbox("Confirmo que deseo eliminar este sprint", key="confirm_delete_sprint")
            if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                try:
                    sprints_service.eliminar(sel_del.id)
                    st.success(f"Sprint '{sel_del.nombre}' eliminado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {str(e)}")
