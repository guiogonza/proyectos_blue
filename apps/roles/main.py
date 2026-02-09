# apps/roles/main.py

import streamlit as st
from infra.repositories import roles_repo
from shared.auth.auth import can_edit
from shared.utils.exports import export_csv


def render():
    st.title("🏷️ Gestión de Roles Principales")
    st.caption("Administra los roles disponibles para asignar a personas")

    # ── Filtros ──────────────────────────────────────────────
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        estado = st.selectbox("Estado", ["Activos", "Inactivos", "Todos"], index=0)
        solo_activos = {"Activos": True, "Inactivos": False, "Todos": None}[estado]
    with col_f2:
        search = st.text_input("Buscar por nombre", placeholder="Escribe para filtrar")

    items = roles_repo.list_roles(solo_activos=solo_activos, search=(search or None))
    st.success(f"Total: {len(items)} rol(es)")

    # ── Exportar ─────────────────────────────────────────────
    col_a1, _ = st.columns([1, 1])
    with col_a1:
        if st.button("📤 Exportar CSV"):
            path = export_csv(items, "roles_principales")
            st.toast(f"Exportado a {path}", icon="✅")

    # ── Tabla ────────────────────────────────────────────────
    if items:
        display = [
            {"ID": r["id"], "Nombre": r["nombre"], "Activo": "✅" if r["activo"] else "❌"}
            for r in items
        ]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No hay roles con ese filtro.")

    # ── CRUD (solo si puede editar) ──────────────────────────
    if not can_edit():
        return

    st.markdown("---")
    st.subheader("➕ Crear / ✏️ Editar / 🗑️ Eliminar")
    tab_create, tab_edit, tab_estado, tab_delete = st.tabs(
        ["Crear rol", "Editar rol", "Activar/Desactivar", "Eliminar"]
    )

    # ── Crear ────────────────────────────────────────────────
    with tab_create:
        with st.form("form_create_rol", clear_on_submit=True):
            nombre = st.text_input("Nombre del rol")
            if st.form_submit_button("Crear"):
                nombre_clean = nombre.strip()
                if not nombre_clean:
                    st.error("El nombre no puede estar vacío.")
                elif roles_repo.get_by_nombre(nombre_clean):
                    st.error(f"Ya existe un rol con el nombre '{nombre_clean}'.")
                else:
                    rid = roles_repo.create_role(nombre_clean)
                    st.success(f"Rol creado con ID {rid}")
                    st.rerun()

    # ── Editar ───────────────────────────────────────────────
    with tab_edit:
        if not items:
            st.info("No hay roles para editar con el filtro actual.")
        else:
            opts = {f"{r['id']} - {r['nombre']}": r for r in items}
            sel_k = st.selectbox("Selecciona rol", list(opts.keys()), key="edit_rol_select")
            sel = opts[sel_k]

            with st.form("form_edit_rol"):
                nombre_e = st.text_input("Nombre", sel["nombre"])
                activo_e = st.checkbox("Activo", value=bool(sel["activo"]))
                if st.form_submit_button("Guardar cambios"):
                    nombre_e_clean = nombre_e.strip()
                    if not nombre_e_clean:
                        st.error("El nombre no puede estar vacío.")
                    else:
                        dup = roles_repo.get_by_nombre(nombre_e_clean)
                        if dup and dup["id"] != sel["id"]:
                            st.error(f"Ya existe otro rol con el nombre '{nombre_e_clean}'.")
                        else:
                            roles_repo.update_role(sel["id"], nombre_e_clean, activo_e)
                            st.success("Cambios guardados")
                            st.rerun()

    # ── Activar / Desactivar ─────────────────────────────────
    with tab_estado:
        if not items:
            st.info("No hay roles disponibles.")
        else:
            opts_e = {f"{r['id']} - {r['nombre']} ({'✅ Activo' if r['activo'] else '❌ Inactivo'})": r for r in items}
            sel_e_k = st.selectbox("Selecciona rol", list(opts_e.keys()), key="estado_rol_select")
            sel_e = opts_e[sel_e_k]
            nuevo_estado = not bool(sel_e["activo"])
            label = "Activar" if nuevo_estado else "Desactivar"
            if st.button(f"{'✅' if nuevo_estado else '❌'} {label} rol"):
                roles_repo.update_role(sel_e["id"], sel_e["nombre"], nuevo_estado)
                st.success(f"Rol '{sel_e['nombre']}' {'activado' if nuevo_estado else 'desactivado'}")
                st.rerun()

    # ── Eliminar ─────────────────────────────────────────────
    with tab_delete:
        st.warning("⚠️ **Advertencia**: Eliminar un rol no afecta las personas que ya lo tienen asignado, "
                   "pero no podrá usarse para nuevas asignaciones.")
        if not items:
            st.info("No hay roles para eliminar.")
        else:
            opts_d = {f"{r['id']} - {r['nombre']}": r for r in items}
            sel_d_k = st.selectbox("Selecciona rol a eliminar", list(opts_d.keys()), key="delete_rol_select")
            sel_d = opts_d[sel_d_k]
            st.error(f"Vas a eliminar: **{sel_d['nombre']}** (ID: {sel_d['id']})")
            confirmar = st.checkbox("Confirmo que deseo eliminar este rol", key="confirm_delete_rol")
            if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                roles_repo.delete_role(sel_d["id"])
                st.success(f"Rol '{sel_d['nombre']}' eliminado")
                st.rerun()
