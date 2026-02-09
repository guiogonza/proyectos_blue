# apps/asignaciones/main.py
import streamlit as st
from datetime import date
from typing import Optional
from domain.schemas.asignaciones import AsignacionCreate, AsignacionUpdate, AsignacionEnd
from domain.services import asignaciones_service
from infra.repositories.proyectos_repo import list_proyectos
from infra.repositories.personas_repo import list_personas
from infra.repositories.sprints_repo import list_sprints
from infra.repositories.perfiles_repo import get_perfiles_para_asignacion
from shared.utils.exports import export_csv
from shared.auth.auth import is_admin, get_user_proyectos, can_edit

def _personas_options():
    rows = list_personas(None, True, None)
    return {f"{r['id']} - {r['nombre']} ({r['ROL_PRINCIPAL']})": r["id"] for r in rows}

def _proyectos_options():
    rows = list_proyectos(estado=None, cliente=None, search=None)
    proyectos_permitidos = get_user_proyectos()
    
    options = {}
    for r in rows:
        if r["ESTADO"] != "Cerrado":
            # Si no es admin, filtrar por proyectos permitidos
            if not is_admin() and proyectos_permitidos and r["id"] not in proyectos_permitidos:
                continue
            options[f"{r['id']} - {r['NOMBRE']} ({r['ESTADO']})"] = r["id"]
    return options

def _sprints_options(proyecto_id: Optional[int] = None):
    """Obtiene opciones de sprints, filtrados por proyecto si se especifica"""
    rows = list_sprints(proyecto_id=proyecto_id, estado=None, search=None)
    options = {"(Sin sprint)": None}
    for r in rows:
        if r["estado"] != "Cerrado":
            # Incluir información del proyecto y actividades si están disponibles
            proyecto_info = f" - Proyecto {r.get('proyecto_id', '')}" if not proyecto_id else ""
            actividades_info = f" - {r.get('actividades', '')[:30]}..." if r.get('actividades') else ""
            options[f"{r['id']} - {r['nombre']} ({r['estado']}){proyecto_info}{actividades_info}"] = r["id"]
    return options

def _perfiles_options():
    """Obtiene opciones de perfiles activos"""
    rows = get_perfiles_para_asignacion()
    options = {"(Sin perfil)": None}
    for r in rows:
        options[r["nombre"]] = r["id"]
    return options

def _clean_items_for_display(items):
    """Elimina persona_id, proyecto_id, sprint_id y perfil_id de los items para mostrar solo los nombres"""
    clean_items = []
    for item in items:
        item_dict = item.dict()
        # Remover los campos de ID que no queremos mostrar
        item_dict.pop('persona_id', None)
        item_dict.pop('proyecto_id', None)
        item_dict.pop('sprint_id', None)
        item_dict.pop('perfil_id', None)
        clean_items.append(item_dict)
    return clean_items

def _assignments_table(persona_id: Optional[int], proyecto_id: Optional[int], solo_activas: Optional[bool]):
    items = asignaciones_service.listar(persona_id, proyecto_id, solo_activas)
    
    # Filtrar por proyectos del usuario si no es admin
    if not is_admin():
        proyectos_permitidos = get_user_proyectos()
        if proyectos_permitidos:
            items = [i for i in items if i.proyecto_id in proyectos_permitidos]
    
    if items:
        # Excluir persona_id y proyecto_id de la visualizaci�n, mantener solo nombres
        display_items = _clean_items_for_display(items)
        st.dataframe(display_items, use_container_width=True, hide_index=True)
    else:
        st.info("No hay asignaciones con el filtro aplicado.")
    return items

def render():
    st.title("Asignaciones Personas - Proyectos/Sprints")

    # ---- Filtros ----
    colf1, colf2, colf3 = st.columns([1.5, 1.5, 1])
    with colf1:
        p_opts = _personas_options()
        persona_sel = st.selectbox("Persona (filtro)", ["(Todas)"] + list(p_opts.keys()))
        persona_id = None if persona_sel == "(Todas)" else p_opts[persona_sel]
    with colf2:
        pr_opts = _proyectos_options()
        proyecto_sel = st.selectbox("Proyecto (filtro)", ["(Todos)"] + list(pr_opts.keys()))
        proyecto_id = None if proyecto_sel == "(Todos)" else pr_opts[proyecto_sel]
    with colf3:
        estado = st.selectbox("Estado asignacion", ["Activas", "Inactivas", "Todas"], index=0)
        solo_activas = {"Activas": True, "Inactivas": False, "Todas": None}[estado]

    items = _assignments_table(persona_id, proyecto_id, solo_activas)

    # Export
    if st.button(" Exportar CSV"):
        # Preparar datos para exportar sin persona_id y proyecto_id
        export_items = _clean_items_for_display(items)
        path = export_csv(export_items, "asignaciones")
        st.toast(f"Exportado a {path}", icon="?")

    st.markdown("---")
    
    # Solo mostrar formularios de edición si el usuario puede editar
    if can_edit():
        st.subheader("➡️ Crear / ✏️ Editar / 📍 Terminar / 🗑️ Eliminar")

        tab_create, tab_edit, tab_end, tab_delete = st.tabs(["Crear", "Editar", "Terminar", "Eliminar"])

        # ---- Crear ----
        with tab_create:
            if not p_opts or not pr_opts:
                st.warning("No hay personas o proyectos disponibles para crear asignaciones.")
            else:
                # Selección de persona y proyecto
                col1, col2 = st.columns(2)
                persona_sel_c = col1.selectbox("Persona", list(p_opts.keys()), key="persona_create")
                proyecto_sel_c = col2.selectbox("Proyecto", list(pr_opts.keys()), key="proyecto_create")

                # Sprint y Perfil
                proyecto_id_sel = pr_opts[proyecto_sel_c]
                sprint_opts = _sprints_options(proyecto_id_sel)

                col_sprint_perfil = st.columns(2)
                with col_sprint_perfil[0]:
                    sprint_fk = st.selectbox("Sprint (opcional)", list(sprint_opts.keys()),
                                             help="Sprints disponibles para el proyecto seleccionado")
                with col_sprint_perfil[1]:
                    perfil_opts = _perfiles_options()
                    perfil_fk = st.selectbox("Perfil", list(perfil_opts.keys()),
                                             help="Selecciona el perfil para esta asignación")

                # País
                PAISES = sorted(["Argentina", "Colombia", "España", "México", "Perú", "Uruguay"])
                pais_seleccionado = st.selectbox(
                    "País", options=PAISES, index=None,
                    placeholder="Escribe para buscar un país...",
                    help="Selecciona el país de la asignación"
                )

                st.markdown("---")

                # --- Filas dinámicas de asignación ---
                if "create_row_ids" not in st.session_state:
                    st.session_state.create_row_ids = [0]
                    st.session_state.create_row_next_id = 1

                # Encabezados
                h1, h2, h3, h4, h5 = st.columns([1, 1, 0.7, 0.7, 0.3])
                h1.markdown("**Fecha inicio**")
                h2.markdown("**Fecha fin**")
                h3.markdown("**Dedicación (h)**")
                h4.markdown("**Tarifa**")
                h5.markdown("")

                # Renderizar cada fila
                row_to_delete = None
                for rid in st.session_state.create_row_ids:
                    c1, c2, c3, c4, c5 = st.columns([1, 1, 0.7, 0.7, 0.3])
                    with c1:
                        st.date_input("fi", value=date.today(), key=f"cr_fi_{rid}", label_visibility="collapsed")
                    with c2:
                        st.date_input("ff", value=None, key=f"cr_ff_{rid}", label_visibility="collapsed")
                    with c3:
                        st.number_input("ded", min_value=1.0, max_value=200.0, value=40.0,
                                        step=1.0, format="%.1f", key=f"cr_ded_{rid}", label_visibility="collapsed")
                    with c4:
                        st.number_input("tar", min_value=0.0, value=0.0,
                                        step=0.01, format="%.2f", key=f"cr_tar_{rid}", label_visibility="collapsed")
                    with c5:
                        if len(st.session_state.create_row_ids) > 1:
                            if st.button("🗑️", key=f"cr_del_{rid}"):
                                row_to_delete = rid

                if row_to_delete is not None:
                    st.session_state.create_row_ids.remove(row_to_delete)
                    st.rerun()

                # Botón agregar línea
                if st.button("➕ Agregar línea"):
                    st.session_state.create_row_ids.append(st.session_state.create_row_next_id)
                    st.session_state.create_row_next_id += 1
                    st.rerun()

                st.markdown("")

                # Botón crear
                if st.button("✅ Crear asignaciones", type="primary"):
                    try:
                        created_ids = []
                        last_info = None
                        for rid in st.session_state.create_row_ids:
                            fi = st.session_state[f"cr_fi_{rid}"]
                            ff = st.session_state.get(f"cr_ff_{rid}")
                            ded = st.session_state[f"cr_ded_{rid}"]
                            tar = st.session_state[f"cr_tar_{rid}"]
                            dto = AsignacionCreate(
                                persona_id=p_opts[persona_sel_c],
                                proyecto_id=pr_opts[proyecto_sel_c],
                                sprint_id=sprint_opts[sprint_fk],
                                perfil_id=perfil_opts[perfil_fk],
                                dedicacion_horas=ded,
                                tarifa=tar if tar > 0 else None,
                                fecha_asignacion=fi,
                                fecha_fin=ff
                            )
                            last_info = asignaciones_service.crear(dto)
                            created_ids.append(last_info['asignacion_id'])
                            if last_info.get("over_projects"):
                                st.warning("La persona quedaría en más proyectos que el umbral configurado.")

                        st.success(f"Se crearon {len(created_ids)} asignación(es) — IDs: {created_ids}. Carga post: {last_info['total_horas_post']:.1f}h")
                        st.session_state.create_row_ids = [0]
                        st.session_state.create_row_next_id = 1
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # ---- Editar ----
        with tab_edit:
            if not items:
                st.info("No hay asignaciones que editar con el filtro actual.")
            else:
                options = {f"{i.id} - {i.persona_nombre} → {i.proyecto_nombre}": i for i in items}
                sel_key = st.selectbox("Selecciona asignacion", list(options.keys()))
                sel = options[sel_key]
                with st.form("form_edit_asig"):
                    col1, col2 = st.columns(2)
                    persona_fk_e = col1.selectbox("Persona", list(p_opts.keys()), index=list(p_opts.values()).index(sel.persona_id))
                    proyecto_fk_e = col2.selectbox("Proyecto", list(pr_opts.keys()), index=list(pr_opts.values()).index(sel.proyecto_id))
                    
                    # Sprint selection for editing - filtrado por el proyecto seleccionado
                    proyecto_id_sel_e = pr_opts[proyecto_fk_e]
                    sprint_opts_e = _sprints_options(proyecto_id_sel_e)
                    current_sprint_key = "(Sin sprint)"
                    if sel.sprint_id:
                        for key, value in sprint_opts_e.items():
                            if value == sel.sprint_id:
                                current_sprint_key = key
                                break
                    
                    # Perfil selection for editing
                    perfil_opts_e = _perfiles_options()
                    current_perfil_key = "(Sin perfil)"
                    if sel.perfil_id:
                        for key, value in perfil_opts_e.items():
                            if value == sel.perfil_id:
                                current_perfil_key = key
                                break
                    
                    col_sprint_perfil_e = st.columns(2)
                    with col_sprint_perfil_e[0]:
                        sprint_fk_e = st.selectbox("Sprint (opcional)", list(sprint_opts_e.keys()), 
                                                 index=list(sprint_opts_e.keys()).index(current_sprint_key),
                                                 help=f"Sprints disponibles para el proyecto seleccionado")
                    with col_sprint_perfil_e[1]:
                        perfil_fk_e = st.selectbox("Perfil", list(perfil_opts_e.keys()), 
                                                  index=list(perfil_opts_e.keys()).index(current_perfil_key),
                                                  help="Selecciona el perfil para esta asignación")
                    
                    col3, col4, col5 = st.columns([1,1,1])
                    dedicacion_e = col3.number_input("Dedicación (horas)", min_value=1.0, max_value=200.0, value=float(sel.dedicacion_horas), step=1.0, format="%.1f")
                    tarifa_e = col4.number_input("Tarifa", min_value=0.0, value=float(sel.tarifa) if sel.tarifa else 0.0, step=0.01, format="%.2f", help="Tarifa por hora")
                    fi_e = col5.date_input("Fecha asignacion", value=sel.fecha_asignacion)
                    ff_e = st.date_input("Fecha fin (opcional)", value=sel.fecha_fin) if st.checkbox("Modificar fecha fin", value=bool(sel.fecha_fin)) else sel.fecha_fin

                    if st.form_submit_button("Guardar cambios"):
                        try:
                            dto = AsignacionUpdate(
                                id=sel.id,
                                persona_id=p_opts[persona_fk_e],
                                proyecto_id=pr_opts[proyecto_fk_e],
                                sprint_id=sprint_opts_e[sprint_fk_e],
                                perfil_id=perfil_opts_e[perfil_fk_e],
                                dedicacion_horas=dedicacion_e,
                                tarifa=tarifa_e if tarifa_e > 0 else None,
                                fecha_asignacion=fi_e,
                                fecha_fin=ff_e
                            )
                            info = asignaciones_service.actualizar(dto)
                            if info.get("over_projects"):
                                st.warning("La persona quedaria en mas proyectos que el umbral configurado.")
                            st.success("Cambios guardados")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        # ---- Terminar ----
        with tab_end:
            activos = [i for i in items if i.fecha_fin is None or i.fecha_fin >= date.today()]
            if not activos:
                st.info("No hay asignaciones activas en el filtro actual.")
            else:
                options2 = {f"{i.id} - {i.persona_nombre} → {i.proyecto_nombre}": i for i in activos}
                sel_key2 = st.selectbox("Selecciona asignacion a terminar", list(options2.keys()))
                sel2 = options2[sel_key2]
                fecha_fin = st.date_input("Fecha fin", value=date.today())
                if st.button("Terminar asignacion"):
                    try:
                        dto = AsignacionEnd(id=sel2.id, fecha_fin=fecha_fin)
                        asignaciones_service.terminar(dto)
                        st.success("Asignacion terminada")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # ---- Eliminar ----
        with tab_delete:
            st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente la asignación de la base de datos.")
            if not items:
                st.info("No hay asignaciones para eliminar con el filtro actual.")
            else:
                options_del = {f"{i.id} - {i.persona_nombre} → {i.proyecto_nombre} ({i.dedicacion_horas}h)": i for i in items}
                sel_del_k = st.selectbox("Selecciona asignación a eliminar", list(options_del.keys()), key="delete_select_asignacion")
                sel_del = options_del[sel_del_k]
                
                st.error(f"**Vas a eliminar:**")
                st.write(f"- **Persona:** {sel_del.persona_nombre}")
                st.write(f"- **Proyecto:** {sel_del.proyecto_nombre}")
                if sel_del.sprint_nombre:
                    st.write(f"- **Sprint:** {sel_del.sprint_nombre}")
                st.write(f"- **Dedicación:** {sel_del.dedicacion_horas} horas")
                st.write(f"- **Fecha asignación:** {sel_del.fecha_asignacion}")
                
                confirmar = st.checkbox("Confirmo que deseo eliminar esta asignación", key="confirm_delete_asignacion")
                if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                    try:
                        asignaciones_service.eliminar(sel_del.id)
                        st.success(f"Asignación eliminada exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {str(e)}")
