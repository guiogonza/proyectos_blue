# apps/perfiles/main.py

import streamlit as st
from datetime import date
from domain.schemas.perfiles import PerfilCreate, PerfilUpdate
from domain.services import perfiles_service
from shared.utils.exports import export_csv
from shared.auth.auth import can_edit

def render():
    st.title("📋 Gestión de Perfiles")
    st.caption("CRUD de perfiles para asignaciones")

    # Filtros
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        estado = st.selectbox("Estado", options=["Activos", "Inactivos", "Todos"], index=0)
        solo_activos = {"Activos": True, "Inactivos": False, "Todos": None}[estado]
    with col_f2:
        search = st.text_input("Buscar por nombre", value="", placeholder="Escribe para filtrar")

    items = perfiles_service.listar(solo_activos=solo_activos, search=(search or None))
    st.success(f"Total: {len(items)} perfil(es)")

    # Exportar
    col_a1, _ = st.columns([1, 1])
    with col_a1:
        if st.button("📤 Exportar CSV"):
            path = export_csv([i.dict() for i in items], "perfiles")
            st.toast(f"Exportado a {path}", icon="✅")

    # Tabla de perfiles
    if items:
        st.dataframe([i.dict() for i in items], use_container_width=True, hide_index=True)
    else:
        st.info("No hay perfiles con ese filtro.")

    # Solo mostrar formularios de edición si el usuario puede editar
    if can_edit():
        st.markdown("---")
        st.subheader("➕ Crear / ✏️ Editar / 🗑️ Eliminar")
        tab_create, tab_edit, tab_estado, tab_delete = st.tabs(["Crear perfil", "Editar perfil", "Activar/Desactivar", "Eliminar"])

        # ---- Crear ----
        with tab_create:
            with st.form("form_create_perfil", clear_on_submit=True):
                nombre = st.text_input("Nombre del perfil", "")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    tarifa = st.number_input("Tarifa sin IVA ($)", min_value=0.0, step=0.01, format="%.2f", key="create_tarifa")
                with col_t2:
                    vigencia = st.date_input("Vigencia", value=date.today(), key="create_vigencia")
                
                if st.form_submit_button("Crear"):
                    try:
                        dto = PerfilCreate(nombre=nombre.strip(), tarifa_sin_iva=tarifa, vigencia=vigencia)
                        perfil_id = perfiles_service.crear(dto)
                        st.success(f"Perfil creado con ID {perfil_id}")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # ---- Editar ----
        with tab_edit:
            options = {f"{i.id} - {i.nombre}": i for i in items}
            if not options:
                st.info("No hay perfiles para editar con el filtro actual.")
            else:
                sel = options[st.selectbox("Selecciona perfil", list(options.keys()))]
                
                with st.form("form_edit_perfil"):
                    nombre_e = st.text_input("Nombre del perfil", sel.nombre)
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        tarifa_e = st.number_input("Tarifa sin IVA ($)", min_value=0.0, step=0.01, format="%.2f", value=float(sel.tarifa_sin_iva) if sel.tarifa_sin_iva else 0.0, key="edit_tarifa")
                    with col_e2:
                        vigencia_e = st.date_input("Vigencia", value=sel.vigencia if sel.vigencia else date.today(), key="edit_vigencia")
                    activo_e = st.checkbox("Activo", value=sel.activo)
                    
                    if st.form_submit_button("Guardar cambios"):
                        try:
                            dto = PerfilUpdate(
                                id=sel.id,
                                nombre=nombre_e.strip(),
                                tarifa_sin_iva=tarifa_e,
                                vigencia=vigencia_e,
                                activo=activo_e
                            )
                            perfiles_service.actualizar(dto)
                            st.success("Cambios guardados")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        # ---- Activar/Desactivar ----
        with tab_estado:
            st.info("💡 **Nota**: Puedes cambiar el estado activo/inactivo directamente desde la pestaña 'Editar'.")
            st.markdown("---")
            options2 = {f"{i.id} - {i.nombre} ({'Activo' if i.activo else 'Inactivo'})": i for i in items}
            if not options2:
                st.info("No hay perfiles en el filtro actual.")
            else:
                sel2 = options2[st.selectbox("Selecciona perfil", list(options2.keys()), key="estado_select")]
                nuevo_estado = st.toggle("Activo", value=sel2.activo)
                if st.button("Aplicar estado"):
                    try:
                        perfiles_service.cambiar_estado(sel2.id, nuevo_estado)
                        st.success("Estado actualizado")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        # ---- Eliminar ----
        with tab_delete:
            st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el perfil de la base de datos.")
            options_del = {f"{i.id} - {i.nombre}": i for i in items}
            if not options_del:
                st.info("No hay perfiles para eliminar con el filtro actual.")
            else:
                sel_del = options_del[st.selectbox("Selecciona perfil a eliminar", list(options_del.keys()), key="delete_select")]
                st.error(f"Vas a eliminar: **{sel_del.nombre}** (ID: {sel_del.id})")
                confirmar = st.checkbox("Confirmo que deseo eliminar este perfil", key="confirm_delete_perfil")
                if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                    try:
                        perfiles_service.eliminar(sel_del.id)
                        st.success(f"Perfil '{sel_del.nombre}' eliminado exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {str(e)}")


# Permite ejecutar este archivo solo (fuera del multipage) para pruebas:
if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(page_title="Perfiles", page_icon="📋", layout="wide")
    render()
