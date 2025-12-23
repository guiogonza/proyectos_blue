# apps/personas/main.py

import streamlit as st
from datetime import date
from domain.schemas.personas import PersonaCreate, PersonaUpdate, ROLES_PERMITIDOS, SENIORITY_PERMITIDOS, TIPOS_DOCUMENTO_PERMITIDOS
from domain.services import personas_service
from shared.utils.exports import export_csv
from shared.auth.auth import can_edit

def render():
    st.title("👤 Gestión de Personas")
    st.caption("CRUD + filtros + activar/desactivar + export CSV + organigrama")

    col_f1, col_f2, col_f3 = st.columns([1,1,2])
    with col_f1:
        rol_filter = st.selectbox("Rol", options=["(Todos)"] + ROLES_PERMITIDOS, index=0)
        rol_filter_val = None if rol_filter == "(Todos)" else rol_filter
    with col_f2:
        estado = st.selectbox("Estado", options=["Activas", "Inactivas", "Todas"], index=0)
        solo_activas = {"Activas": True, "Inactivas": False, "Todas": None}[estado]
    with col_f3:
        search = st.text_input("Buscar por nombre/rol", value="", placeholder="Escribe para filtrar")

    items = personas_service.listar(rol=rol_filter_val, solo_activas=solo_activas, search=(search or None))
    st.success(f"Total: {len(items)} registro(s)")

    col_a1, _ = st.columns([1,1])
    with col_a1:
        if st.button("📤 Exportar CSV"):
            path = export_csv([i.dict() for i in items], "personas")
            st.toast(f"Exportado a {path}", icon="✅")

    if items:
        st.dataframe([i.dict() for i in items], use_container_width=True, hide_index=True)
    else:
        st.info("No hay personas con ese filtro.")

    # Solo mostrar formularios de edición si el usuario puede editar
    if can_edit():
        st.markdown("---")
        st.subheader("➕ Crear / ✏️ Editar / 🗑️ Eliminar")
        tab_create, tab_edit, tab_estado, tab_delete = st.tabs(["Crear persona", "Editar persona", "Activar/Desactivar", "Eliminar"])

        with tab_create:
            # Obtener personas para selector de líder
            personas_lider = personas_service.get_personas_para_lider()
            opciones_lider_nombres = [p["nombre"] for p in personas_lider]
            opciones_lider_dict = {p["nombre"]: p["id"] for p in personas_lider}
            
            # Selector de líder FUERA del formulario - empieza vacío para escribir
            lider_sel = st.selectbox("Líder Directo (opcional)", 
                                     options=opciones_lider_nombres,
                                     index=None, 
                                     key="lider_create",
                                     placeholder="Escribe para buscar...")
            lider_id = opciones_lider_dict.get(lider_sel) if lider_sel else None
            
            with st.form("form_create", clear_on_submit=True):
                c1, c2, c3 = st.columns([2,1,1])
                nombre = c1.text_input("Nombre", "")
                rol = c2.selectbox("Rol Principal", options=ROLES_PERMITIDOS, index=0)
                tarifa = c3.number_input("Costo Recurso (opcional)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")
                
                # Segunda fila: documento, contacto, correo
                c4, c5, c6 = st.columns([1,1,1])
                tipo_doc = c4.selectbox("Tipo Documento", options=TIPOS_DOCUMENTO_PERMITIDOS, index=0)
                numero_doc = c5.text_input("Número Documento (opcional)", "")
                numero_contacto = c6.text_input("Número de contacto (opcional)", "")
                
                # Tercera fila: país, seniority
                c7, c8, c9 = st.columns([1,1,1])
                correo = c7.text_input("Correo electrónico (opcional)", "")
                pais = c8.text_input("País (opcional)", "")
                seniority = c9.selectbox("Seniority", options=SENIORITY_PERMITIDOS, index=0)
                
                # Cuarta fila: vigencia
                c10, _, _ = st.columns([1,1,1])
                vigencia = c10.number_input("Vigencia (año)", min_value=1900, max_value=2100, value=date.today().year, step=1,
                                           help="Año de vigencia del colaborador")
                
                st.caption(f"Líder seleccionado: **{lider_sel or 'Sin líder'}**")
                
                if st.form_submit_button("Crear"):
                    try:
                        dto = PersonaCreate(
                            nombre=nombre.strip(), 
                            ROL_PRINCIPAL=rol, 
                            COSTO_RECURSO=(tarifa if tarifa > 0 else None),
                            NUMERO_DOCUMENTO=numero_doc.strip() if numero_doc.strip() else None,
                            numero_contacto=numero_contacto.strip() if numero_contacto.strip() else None,
                            correo=correo.strip() if correo.strip() else None,
                            PAIS=pais.strip() if pais.strip() else None,
                            SENIORITY=seniority,
                            LIDER_DIRECTO=lider_id,
                            TIPO_DOCUMENTO=tipo_doc,
                            vigencia=vigencia
                        )
                        personas_service.crear(dto)
                        st.success("Creada")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        with tab_edit:
            # Obtener personas para selector de líder (excluyendo la persona actual en edición)
            personas_lider = personas_service.get_personas_para_lider()
            
            options = {f"{i.id} - {i.nombre} ({i.ROL_PRINCIPAL})": i for i in items}
            if not options:
                st.info("No hay registros para editar con el filtro actual.")
            else:
                sel = options[st.selectbox("Selecciona persona", list(options.keys()))]
                
                # Filtrar opciones de líder para excluir la persona actual (evitar auto-referencia)
                opciones_lider_nombres_e = [p["nombre"] for p in personas_lider if p["id"] != sel.id]
                opciones_lider_dict_e = {p["nombre"]: p["id"] for p in personas_lider if p["id"] != sel.id}
                
                # Determinar líder actual
                lider_actual_nombre = None
                if sel.LIDER_DIRECTO:
                    for nombre_l, id_l in opciones_lider_dict_e.items():
                        if id_l == sel.LIDER_DIRECTO:
                            lider_actual_nombre = nombre_l
                            break
                
                # Selector de líder FUERA del formulario - empieza vacío o con valor actual
                lider_idx_e = None
                if lider_actual_nombre and lider_actual_nombre in opciones_lider_nombres_e:
                    lider_idx_e = opciones_lider_nombres_e.index(lider_actual_nombre)
                lider_sel_e = st.selectbox("Líder Directo (opcional)", 
                                          options=opciones_lider_nombres_e,
                                          index=lider_idx_e, 
                                          key="lider_edit",
                                          placeholder="Escribe para buscar...")
                lider_id_e = opciones_lider_dict_e.get(lider_sel_e) if lider_sel_e else None
                
                with st.form("form_edit"):
                    c1, c2, c3 = st.columns([2,1,1])
                    nombre_e = c1.text_input("Nombre", sel.nombre)
                    rol_e = c2.selectbox("Rol Principal", options=ROLES_PERMITIDOS, index=(ROLES_PERMITIDOS.index(sel.ROL_PRINCIPAL) if sel.ROL_PRINCIPAL in ROLES_PERMITIDOS else 0))
                    tarifa_e = c3.number_input("Costo Recurso (opcional)", min_value=0.0, value=float(sel.COSTO_RECURSO or 0.0), step=1000.0, format="%.2f")
                    
                    # Segunda fila: documento, contacto, correo
                    c4, c5, c6 = st.columns([1,1,1])
                    tipo_doc_e = c4.selectbox("Tipo Documento", options=TIPOS_DOCUMENTO_PERMITIDOS, 
                                             index=(TIPOS_DOCUMENTO_PERMITIDOS.index(sel.TIPO_DOCUMENTO) if sel.TIPO_DOCUMENTO and sel.TIPO_DOCUMENTO in TIPOS_DOCUMENTO_PERMITIDOS else 0))
                    numero_doc_e = c5.text_input("Número Documento (opcional)", sel.NUMERO_DOCUMENTO or "")
                    numero_contacto_e = c6.text_input("Número de contacto (opcional)", sel.numero_contacto or "")
                    
                    # Tercera fila: país, seniority, correo
                    c7, c8, c9 = st.columns([1,1,1])
                    correo_e = c7.text_input("Correo electrónico (opcional)", sel.correo or "")
                    pais_e = c8.text_input("País (opcional)", sel.PAIS or "")
                    seniority_e = c9.selectbox("Seniority", options=SENIORITY_PERMITIDOS, 
                                              index=(SENIORITY_PERMITIDOS.index(sel.SENIORITY) if sel.SENIORITY and sel.SENIORITY in SENIORITY_PERMITIDOS else 0))
                    
                    # Cuarta fila: vigencia
                    c10, _, _ = st.columns([1,1,1])
                    vigencia_e = c10.number_input("Vigencia (año)", min_value=1900, max_value=2100, 
                                                  value=int(sel.vigencia) if sel.vigencia else date.today().year, step=1,
                                                  help="Año de vigencia del colaborador")
                    
                    st.caption(f"Líder seleccionado: **{lider_sel_e or 'Sin líder'}**")
                    
                    # Campo de estado activo/inactivo
                    activo_e = st.checkbox("Activo", value=sel.activo, help="Desmarcar para desactivar la persona")
                    
                    if st.form_submit_button("Guardar cambios"):
                        try:
                            dto = PersonaUpdate(
                                id=sel.id, 
                                nombre=nombre_e.strip(), 
                                ROL_PRINCIPAL=rol_e, 
                                COSTO_RECURSO=(tarifa_e if tarifa_e > 0 else None),
                                NUMERO_DOCUMENTO=numero_doc_e.strip() if numero_doc_e.strip() else None,
                                numero_contacto=numero_contacto_e.strip() if numero_contacto_e.strip() else None,
                                correo=correo_e.strip() if correo_e.strip() else None,
                                PAIS=pais_e.strip() if pais_e.strip() else None,
                                SENIORITY=seniority_e,
                                LIDER_DIRECTO=lider_id_e,
                                TIPO_DOCUMENTO=tipo_doc_e,
                                activo=activo_e,
                                vigencia=vigencia_e
                            )
                            personas_service.actualizar(dto)
                            st.success("Cambios guardados")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        with tab_estado:
            st.info("💡 **Nota**: Ahora puedes cambiar el estado activo/inactivo directamente desde la pestaña 'Editar' usando el checkbox.")
            st.markdown("---")
            options2 = {f"{i.id} - {i.nombre} ({'Activa' if i.activo else 'Inactiva'})": i for i in items}
            if not options2:
                st.info("No hay registros en el filtro actual.")
            else:
                sel2 = options2[st.selectbox("Selecciona persona", list(options2.keys()))]
                nuevo_estado = st.toggle("Activo", value=sel2.activo)
                if st.button("Aplicar estado"):
                    try:
                        personas_service.cambiar_estado(sel2.id, nuevo_estado)
                        st.success("Estado actualizado")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        with tab_delete:
            st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente la persona de la base de datos.")
            options_del = {f"{i.id} - {i.nombre} ({i.ROL_PRINCIPAL})": i for i in items}
            if not options_del:
                st.info("No hay registros para eliminar con el filtro actual.")
            else:
                sel_del = options_del[st.selectbox("Selecciona persona a eliminar", list(options_del.keys()), key="delete_select")]
                st.error(f"Vas a eliminar: **{sel_del.nombre}** (ID: {sel_del.id})")
                confirmar = st.checkbox("Confirmo que deseo eliminar esta persona", key="confirm_delete_persona")
                if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                    try:
                        personas_service.eliminar(sel_del.id)
                        st.success(f"Persona '{sel_del.nombre}' eliminada exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {str(e)}")

# Permite ejecutar este archivo solo (fuera del multipage) para pruebas:
if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="Personas", page_icon="👤", layout="wide")
    render()
