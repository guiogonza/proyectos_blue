# apps/proyectos/main.py
import streamlit as st
from datetime import date
from domain.schemas.proyectos import ProyectoCreate, ProyectoUpdate, ProyectoClose, ESTADOS_PROY
from domain.services import proyectos_service, personas_service
from shared.utils.exports import export_csv
from shared.auth.auth import is_admin, get_user_proyectos, can_edit

def _header_resumen(items):
    tot = len(items)
    activos = sum(1 for x in items if x.ESTADO == "Activo")
    cerrados = sum(1 for x in items if x.ESTADO == "Cerrado")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", tot)
    col2.metric("Activos", activos)
    col3.metric("Cerrados", cerrados)

def _filtrar_por_usuario(items):
    """Filtra proyectos según los permisos del usuario"""
    if is_admin():
        return items  # Admin ve todos
    
    proyectos_permitidos = get_user_proyectos()
    if not proyectos_permitidos:
        return []  # Usuario sin proyectos asignados
    
    return [p for p in items if p.id in proyectos_permitidos]

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
    
    # Filtrar por proyectos del usuario
    items = _filtrar_por_usuario(items)
    
    _header_resumen(items)

    # Export
    if st.button("📤 Exportar CSV"):
        path = export_csv([i.dict() for i in items], "proyectos")
        st.toast(f"Exportado a {path}", icon="✅")

    # Tabla (ocultar pm_id y renombrar lider_nombre)
    if items:
        display_items = []
        for i in items:
            item_dict = i.dict()
            item_dict.pop('pm_id', None)  # Ocultar pm_id
            # Renombrar lider_nombre a Líder para mejor visualización
            if 'lider_nombre' in item_dict:
                item_dict['Líder'] = item_dict.pop('lider_nombre') or ""
            display_items.append(item_dict)
        st.dataframe(display_items, use_container_width=True, hide_index=True)
    else:
        st.info("No hay proyectos con ese filtro.")

    # Solo mostrar formularios de edición si el usuario puede editar
    if can_edit():
        st.markdown("---")
        st.subheader("➕ Crear / ✏️ Editar / ✅ Cerrar / 🗑️ Eliminar")

        tab_create, tab_edit, tab_close, tab_delete = st.tabs(["Crear", "Editar", "Cerrar", "Eliminar"])

    # ---- Crear ----
    with tab_create:
        # Lista de países ordenada alfabéticamente
        PAISES = [
            "Argentina",
            "Colombia",
            "España",
            "México",
            "Perú",
            "Uruguay"
        ]
        
        with st.form("form_create_proj", clear_on_submit=True):
            col1, col2 = st.columns([2,2])
            nombre = col1.text_input("Nombre", "")
            cliente = col2.text_input("Cliente (opcional)", "")
            
            col3, col4, col5 = st.columns([1,1,1])
            fi = col3.date_input("Fecha Inicio", value=date.today())
            ff = col4.date_input("Fecha Fin Estimada", value=date.today())
            estado_c = col5.selectbox("Estado", options=ESTADOS_PROY, index=0)
            
            col6, col7, col8 = st.columns([1,1,1])
            costo_est = col6.number_input("Budget", min_value=0.0, value=0.0, step=100000.0, format="%.2f")
            pais = col7.selectbox("País", options=["(Sin país)"] + PAISES, index=0)
            pais_val = None if pais == "(Sin país)" else pais
            categoria = col8.text_input("Categoría (opcional)", "")
            
            col9, col10, col11 = st.columns([1,1,1])
            lider_bt = col9.text_input("Líder Bluetab (opcional)", "")
            lider_cl = col10.text_input("Líder Cliente (opcional)", "")
            manager_bt = col11.text_input("Manager Bluetab (opcional)", "")
            
            fecha_fin = st.date_input("Fecha Fin Real (opcional)", value=None)
            
            # Obtener personas activas para seleccionar líder
            personas = personas_service.listar(rol=None, solo_activas=True, search=None)
            personas_opts = {f"{p.nombre}": p.id for p in personas}
            lider_label = st.selectbox("Líder (opcional)", ["(Sin líder)"] + list(personas_opts.keys()),
                                       help="Escribe para buscar...")
            lider_id = None if lider_label == "(Sin líder)" else personas_opts[lider_label]
            
            if st.form_submit_button("Crear"):
                try:
                    dto = ProyectoCreate(
                        NOMBRE=nombre.strip(),
                        cliente=(cliente.strip() or None),
                        pm_id=lider_id,
                        FECHA_INICIO=fi,
                        FECHA_FIN_ESTIMADA=ff,
                        ESTADO=estado_c,
                        BUDGET=costo_est,
                        PAIS=pais_val,
                        CATEGORIA=(categoria.strip() or None),
                        LIDER_BLUETAB=(lider_bt.strip() or None),
                        LIDER_CLIENTE=(lider_cl.strip() or None),
                        FECHA_FIN=fecha_fin,
                        MANAGER_BLUETAB=(manager_bt.strip() or None)
                    )
                    pid = proyectos_service.crear(dto)
                    st.success(f"Proyecto creado ID {pid}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ---- Editar ----
    with tab_edit:
        options = {f"{i.id} - {i.NOMBRE} ({i.ESTADO})": i for i in items}
        if not options:
            st.info("No hay proyectos para editar con el filtro actual.")
        else:
            sel_key = st.selectbox("Selecciona proyecto", list(options.keys()))
            sel = options[sel_key]
            with st.form("form_edit_proj"):
                col1, col2 = st.columns([2,2])
                nombre_e = col1.text_input("Nombre", sel.NOMBRE)
                cliente_e = col2.text_input("Cliente", sel.cliente or "")
                
                col3, col4, col5 = st.columns([1,1,1])
                fi_e = col3.date_input("Fecha Inicio", value=sel.FECHA_INICIO)
                ff_e = col4.date_input("Fecha Fin Estimada", value=sel.FECHA_FIN_ESTIMADA)
                estado_e = col5.selectbox("Estado", options=ESTADOS_PROY, index=ESTADOS_PROY.index(sel.ESTADO))
                
                col6, col7, col8 = st.columns([1,1,1])
                costo_e = col6.number_input("Budget", min_value=0.0, value=float(sel.BUDGET), step=100000.0, format="%.2f")
                # Determinar índice del país actual
                pais_idx = 0
                if sel.PAIS and sel.PAIS in PAISES:
                    pais_idx = PAISES.index(sel.PAIS) + 1
                pais_e = col7.selectbox("País", options=["(Sin país)"] + PAISES, index=pais_idx)
                pais_val_e = None if pais_e == "(Sin país)" else pais_e
                categoria_e = col8.text_input("Categoría (opcional)", sel.CATEGORIA or "")
                
                col9, col10, col11 = st.columns([1,1,1])
                lider_bt_e = col9.text_input("Líder Bluetab (opcional)", sel.LIDER_BLUETAB or "")
                lider_cl_e = col10.text_input("Líder Cliente (opcional)", sel.LIDER_CLIENTE or "")
                manager_bt_e = col11.text_input("Manager Bluetab (opcional)", sel.MANAGER_BLUETAB or "")
                
                fecha_fin_e = st.date_input("Fecha Fin Real (opcional)", value=sel.FECHA_FIN)
                
                # Obtener personas activas para seleccionar líder
                personas = personas_service.listar(rol=None, solo_activas=True, search=None)
                personas_opts = {f"{p.nombre}": p.id for p in personas}
                # Determinar líder actual
                lider_actual = "(Sin líder)"
                if sel.pm_id:
                    for nombre_p, id_p in personas_opts.items():
                        if id_p == sel.pm_id:
                            lider_actual = nombre_p
                            break
                lider_idx = 0
                if lider_actual != "(Sin líder)" and lider_actual in list(personas_opts.keys()):
                    lider_idx = list(personas_opts.keys()).index(lider_actual) + 1
                lider_label_e = st.selectbox("Líder (opcional)", ["(Sin líder)"] + list(personas_opts.keys()), 
                                            index=lider_idx, help="Escribe para buscar...")
                lider_id_e = None if lider_label_e == "(Sin líder)" else personas_opts[lider_label_e]
                
                if st.form_submit_button("Guardar cambios"):
                    try:
                        dto = ProyectoUpdate(
                            id=sel.id,
                            NOMBRE=nombre_e.strip(),
                            cliente=(cliente_e.strip() or None),
                            pm_id=lider_id_e,
                            FECHA_INICIO=fi_e,
                            FECHA_FIN_ESTIMADA=ff_e,
                            ESTADO=estado_e,
                            BUDGET=costo_e,
                            PAIS=pais_val_e,
                            CATEGORIA=(categoria_e.strip() or None),
                            LIDER_BLUETAB=(lider_bt_e.strip() or None),
                            LIDER_CLIENTE=(lider_cl_e.strip() or None),
                            FECHA_FIN=fecha_fin_e,
                            MANAGER_BLUETAB=(manager_bt_e.strip() or None)
                        )
                        proyectos_service.actualizar(dto)
                        st.success("Cambios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    # ---- Cerrar ----
    with tab_close:
        options2 = {f"{i.id} - {i.NOMBRE} ({i.ESTADO})": i for i in items if i.ESTADO != "Cerrado"}
        if not options2:
            st.info("No hay proyectos abiertos para cerrar.")
        else:
            sel_key2 = st.selectbox("Selecciona proyecto a cerrar", list(options2.keys()))
            sel2 = options2[sel_key2]
            costo_real = st.number_input("Costo Real Total", min_value=0.0, value=float(sel2.BUDGET), step=100000.0, format="%.2f")
            if st.button("Cerrar proyecto"):
                try:
                    dto = ProyectoClose(id=sel2.id, COSTO_REAL_TOTAL=costo_real)
                    proyectos_service.cerrar(dto)
                    st.success("Proyecto cerrado")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ---- Eliminar ----
    with tab_delete:
        st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el proyecto y todos sus sprints y asignaciones asociadas.")
        options_del = {f"{i.id} - {i.NOMBRE} ({i.ESTADO})": i for i in items}
        if not options_del:
            st.info("No hay proyectos para eliminar con el filtro actual.")
        else:
            sel_del = options_del[st.selectbox("Selecciona proyecto a eliminar", list(options_del.keys()), key="delete_select_proyecto")]
            st.error(f"Vas a eliminar: **{sel_del.NOMBRE}** (ID: {sel_del.id})")
            confirmar = st.checkbox("Confirmo que deseo eliminar este proyecto", key="confirm_delete_proyecto")
            if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                try:
                    proyectos_service.eliminar(sel_del.id)
                    st.success(f"Proyecto '{sel_del.NOMBRE}' eliminado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {str(e)}")
