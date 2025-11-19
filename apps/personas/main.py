# apps/personas/main.py

import streamlit as st
from domain.schemas.personas import PersonaCreate, PersonaUpdate, ROLES_PERMITIDOS
from domain.services import personas_service
from shared.utils.exports import export_csv

def render():
    st.title("👤 Gestión de Personas")
    st.caption("CRUD + filtros + activar/desactivar + export CSV")

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

    st.markdown("---")
    st.subheader("➕ Crear / ✏️ Editar / 🗑️ Eliminar")
    tab_create, tab_edit, tab_estado, tab_delete = st.tabs(["Crear persona", "Editar persona", "Activar/Desactivar", "Eliminar"])

    with tab_create:
        with st.form("form_create", clear_on_submit=True):
            c1, c2, c3 = st.columns([2,1,1])
            nombre = c1.text_input("Nombre", "")
            rol = c2.selectbox("Rol", options=ROLES_PERMITIDOS, index=0)
            tarifa = c3.number_input("Tarifa interna (opcional)", min_value=0.0, value=0.0, step=1000.0, format="%.2f")
            
            # Campos de contacto
            c4, c5, c6 = st.columns([1,1,1])
            cedula = c4.text_input("Cédula (opcional)", "")
            numero_contacto = c5.text_input("Número de contacto (opcional)", "")
            correo = c6.text_input("Correo electrónico (opcional)", "")
            
            if st.form_submit_button("Crear"):
                try:
                    dto = PersonaCreate(
                        nombre=nombre.strip(), 
                        rol=rol, 
                        tarifa_interna=(tarifa if tarifa > 0 else None),
                        cedula=cedula.strip() if cedula.strip() else None,
                        numero_contacto=numero_contacto.strip() if numero_contacto.strip() else None,
                        correo=correo.strip() if correo.strip() else None
                    )
                    personas_service.crear(dto)
                    st.success("Creada")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        options = {f"{i.id} - {i.nombre} ({i.rol})": i for i in items}
        if not options:
            st.info("No hay registros para editar con el filtro actual.")
        else:
            sel = options[st.selectbox("Selecciona persona", list(options.keys()))]
            with st.form("form_edit"):
                c1, c2, c3 = st.columns([2,1,1])
                nombre_e = c1.text_input("Nombre", sel.nombre)
                rol_e = c2.selectbox("Rol", options=ROLES_PERMITIDOS, index=(ROLES_PERMITIDOS.index(sel.rol) if sel.rol in ROLES_PERMITIDOS else 0))
                tarifa_e = c3.number_input("Tarifa interna (opcional)", min_value=0.0, value=float(sel.tarifa_interna or 0.0), step=1000.0, format="%.2f")
                
                # Campos de contacto para edición
                c4, c5, c6 = st.columns([1,1,1])
                cedula_e = c4.text_input("Cédula (opcional)", sel.cedula or "")
                numero_contacto_e = c5.text_input("Número de contacto (opcional)", sel.numero_contacto or "")
                correo_e = c6.text_input("Correo electrónico (opcional)", sel.correo or "")
                
                # Campo de estado activo/inactivo
                activo_e = st.checkbox("Activo", value=sel.activo, help="Desmarcar para desactivar la persona")
                
                if st.form_submit_button("Guardar cambios"):
                    try:
                        dto = PersonaUpdate(
                            id=sel.id, 
                            nombre=nombre_e.strip(), 
                            rol=rol_e, 
                            tarifa_interna=(tarifa_e if tarifa_e > 0 else None),
                            cedula=cedula_e.strip() if cedula_e.strip() else None,
                            numero_contacto=numero_contacto_e.strip() if numero_contacto_e.strip() else None,
                            correo=correo_e.strip() if correo_e.strip() else None,
                            activo=activo_e
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
        options_del = {f"{i.id} - {i.nombre} ({i.rol})": i for i in items}
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
