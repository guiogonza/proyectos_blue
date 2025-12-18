# apps/usuarios/main.py
import streamlit as st
from domain.schemas.usuarios import UsuarioCreate, UsuarioUpdate
from domain.services import usuarios_service, proyectos_service
from infra.repositories import personas_repo
from shared.utils.exports import export_csv

def _personas_opts():
    rows = personas_repo.list_personas(None, True, None)
    return {"(Sin persona ligada)": None, **{f"{r['id']} - {r['nombre']} ({r['ROL_PRINCIPAL']})": r["id"] for r in rows}}

def _proyectos_opts():
    proyectos = proyectos_service.listar(None, None, None)
    return {f"{p.id} - {p.NOMBRE}": p.id for p in proyectos}

def render():
    st.title("🔑 Gestión de Usuarios (admin)")
    items = usuarios_service.listar()

    # Acciones
    cA, cB = st.columns([1,1])
    with cA:
        if st.button("📤 Exportar CSV"):
            from datetime import datetime
            path = export_csv([i.dict() for i in items], "usuarios")
            st.toast(f"Exportado a {path}", icon="✅")

    # Tabla
    if items:
        st.dataframe([{
            **i.dict(),
        } for i in items], use_container_width=True, hide_index=True)
    else:
        st.info("No hay usuarios.")

    st.markdown("---")
    st.subheader("➡️ Crear / ✏️ Editar / � Asignar Proyectos / 🔁 Reset contraseña / 🗑️ Eliminar")

    tab_crear, tab_edit, tab_proyectos, tab_reset, tab_delete = st.tabs(["Crear", "Editar", "Asignar Proyectos", "Reset contraseña", "Eliminar"])

    with tab_crear:
        with st.form("form_user_create", clear_on_submit=True):
            email = st.text_input("Email")
            rol = st.selectbox("Rol", ["admin", "viewer"])
            p_opts = _personas_opts()
            persona_lbl = st.selectbox("Persona (opcional)", list(p_opts.keys()))
            pwd = st.text_input("Contraseña inicial", type="password")
            if st.form_submit_button("Crear"):
                try:
                    dto = UsuarioCreate(email=email.strip(), rol_app=rol, persona_id=p_opts[persona_lbl], password_plain=pwd)
                    uid = usuarios_service.crear(dto)
                    st.success(f"Usuario creado (ID {uid})")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with tab_edit:
        if not items:
            st.info("No hay usuarios para editar.")
        else:
            opt = {f"{i.id} - {i.email} ({i.rol_app})": i for i in items}
            sel_k = st.selectbox("Selecciona usuario", list(opt.keys()))
            sel = opt[sel_k]
            with st.form("form_user_edit"):
                email_e = st.text_input("Email", sel.email)
                rol_e = st.selectbox("Rol", ["admin", "viewer"], index=0 if sel.rol_app=="admin" else 1)
                p_opts = _personas_opts()
                persona_lbl_e = st.selectbox("Persona (opcional)", list(p_opts.keys()), index=0)
                activo_e = st.toggle("Activo", value=sel.activo)
                if st.form_submit_button("Guardar cambios"):
                    try:
                        dto = UsuarioUpdate(id=sel.id, email=email_e.strip(), rol_app=rol_e, persona_id=p_opts[persona_lbl_e], activo=activo_e)
                        usuarios_service.actualizar(dto)
                        st.success("Cambios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    with tab_proyectos:
        st.info("📁 Asigna proyectos a usuarios tipo 'viewer'. Los usuarios admin tienen acceso a todos los proyectos automáticamente.")
        
        # Filtrar solo usuarios viewer
        usuarios_viewer = [i for i in items if i.rol_app.lower() == "viewer"]
        
        if not usuarios_viewer:
            st.warning("No hay usuarios con rol 'viewer'. Los usuarios admin ya tienen acceso a todos los proyectos.")
        else:
            opt_user = {f"{i.id} - {i.email}": i for i in usuarios_viewer}
            sel_user_k = st.selectbox("Selecciona usuario", list(opt_user.keys()), key="proyectos_user_select")
            sel_user = opt_user[sel_user_k]
            
            # Obtener proyectos actuales del usuario
            proyectos_actuales = usuarios_service.get_proyectos_usuario(sel_user.id)
            
            # Obtener todos los proyectos
            proy_opts = _proyectos_opts()
            
            if not proy_opts:
                st.warning("No hay proyectos creados aún.")
            else:
                st.caption(f"Proyectos actualmente asignados: {len(proyectos_actuales)}")
                
                # Multiselect para asignar proyectos
                proy_labels_actuales = [k for k, v in proy_opts.items() if v in proyectos_actuales]
                
                with st.form("form_asignar_proyectos"):
                    proyectos_seleccionados = st.multiselect(
                        "Proyectos asignados",
                        options=list(proy_opts.keys()),
                        default=proy_labels_actuales,
                        help="Selecciona los proyectos a los que este usuario tendrá acceso"
                    )
                    
                    if st.form_submit_button("💾 Guardar asignación"):
                        try:
                            proyecto_ids = [proy_opts[lbl] for lbl in proyectos_seleccionados]
                            usuarios_service.set_proyectos_usuario(sel_user.id, proyecto_ids)
                            st.success(f"Proyectos asignados: {len(proyecto_ids)}")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

    with tab_reset:
        if not items:
            st.info("No hay usuarios para reset.")
        else:
            opt2 = {f"{i.id} - {i.email}": i for i in items}
            sel2_k = st.selectbox("Usuario a resetear", list(opt2.keys()))
            newpwd = st.text_input("Nueva contraseña", type="password")
            if st.button("Aplicar reset"):
                try:
                    usuarios_service.reset_password(opt2[sel2_k].id, newpwd)
                    st.success("Contraseña actualizada.")
                except Exception as e:
                    st.error(str(e))

    with tab_delete:
        st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el usuario de la base de datos.")
        if not items:
            st.info("No hay usuarios para eliminar.")
        else:
            opt_del = {f"{i.id} - {i.email} ({i.rol_app})": i for i in items}
            sel_del_k = st.selectbox("Selecciona usuario a eliminar", list(opt_del.keys()), key="delete_select_usuario")
            sel_del = opt_del[sel_del_k]
            st.error(f"Vas a eliminar: **{sel_del.email}** (ID: {sel_del.id})")
            confirmar = st.checkbox("Confirmo que deseo eliminar este usuario", key="confirm_delete_usuario")
            if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                try:
                    usuarios_service.eliminar(sel_del.id)
                    st.success(f"Usuario '{sel_del.email}' eliminado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {str(e)}")
