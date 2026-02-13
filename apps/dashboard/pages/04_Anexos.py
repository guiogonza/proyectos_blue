# apps/dashboard/pages/04_Anexos.py
import streamlit as st
import os
from datetime import datetime, date
from domain.schemas.documentos import DocumentoCreate, DocumentoUpdate
from domain.services import documentos_service, proyectos_service, personas_service
from shared.auth.auth import require_authentication, is_admin, get_user_proyectos, can_edit, init_auth

# IMPORTANTE: Inicializar autenticación para restaurar sesión desde cookie
init_auth()

require_authentication()

st.title("📎 Gestión de Anexos")
st.caption("Carga y gestiona anexos asociados a proyectos")

# Crear directorio de uploads si no existe
UPLOAD_DIR = "uploads/documentos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Obtener proyectos permitidos para el usuario
proyectos_permitidos = get_user_proyectos()

# Filtros
col1, col2 = st.columns([1, 2])
with col1:
    proyectos = proyectos_service.listar(None, None, None)
    # Filtrar proyectos si no es admin
    if not is_admin() and proyectos_permitidos:
        proyectos = [p for p in proyectos if p.id in proyectos_permitidos]
    proyecto_opts = {f"{p.id} - {p.NOMBRE}": p.id for p in proyectos}
    proyecto_filter = st.selectbox("Filtrar por Proyecto", ["(Todos)"] + list(proyecto_opts.keys()))
    proyecto_id_filter = None if proyecto_filter == "(Todos)" else proyecto_opts[proyecto_filter]

with col2:
    search = st.text_input("Buscar por nombre o descripción", placeholder="Buscar...")

# Listar documentos
items = documentos_service.listar(proyecto_id=proyecto_id_filter, search=(search or None))

# Filtrar por proyectos del usuario si no es admin
if not is_admin() and proyectos_permitidos:
    items = [d for d in items if d.proyecto_id in proyectos_permitidos]

st.success(f"Total: {len(items)} anexo(s)")

# URL base de la API para documentos
API_BASE_URL = "http://164.68.118.86:8502/api/documentos"

if items:
    # Opciones de paginación
    col_pag1, col_pag2, col_pag3 = st.columns([1, 1, 2])
    with col_pag1:
        registros_por_pagina = st.selectbox("Registros por página", [10, 20, 50, 100], index=0)
    
    # Calcular paginación
    total_registros = len(items)
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
    
    with col_pag2:
        pagina_actual = st.number_input("Página", min_value=1, max_value=max(1, total_paginas), value=1, step=1)
    
    with col_pag3:
        st.caption(f"Mostrando página {pagina_actual} de {total_paginas}")
    
    # Aplicar paginación
    inicio = (pagina_actual - 1) * registros_por_pagina
    fin = inicio + registros_por_pagina
    items_pagina = items[inicio:fin]
    
    # Preparar datos para mostrar
    display_data = []
    for doc in items_pagina:
        # Formatear tamaño
        if doc.tamanio_bytes:
            if doc.tamanio_bytes < 1024:
                size_str = f"{doc.tamanio_bytes} B"
            elif doc.tamanio_bytes < 1024 * 1024:
                size_str = f"{doc.tamanio_bytes / 1024:.1f} KB"
            else:
                size_str = f"{doc.tamanio_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = "N/A"
        
        # Formatear valor
        valor_str = f"${doc.valor:,.2f}" if doc.valor else ""
        
        # Formatear IVA
        iva_str = f"${doc.iva:,.2f}" if doc.iva else ""
        
        # Formatear fecha documento
        fecha_doc_str = doc.fecha_documento.strftime("%Y-%m-%d") if doc.fecha_documento else ""
        
        display_data.append({
            "ID": doc.id,
            "Proyecto": doc.proyecto_nombre or f"ID {doc.proyecto_id}",
            "Nombre Archivo": doc.nombre_archivo,
            "Ver": f"{API_BASE_URL}/{doc.id}/view",
            "Descripción": doc.descripcion or "",
            "Valor": valor_str,
            "IVA": iva_str,
            "Fecha Doc": fecha_doc_str,
            "Tamaño": size_str,
            "Fecha Carga": doc.fecha_carga.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Mostrar tabla con links clicables
    st.dataframe(
        display_data, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Ver": st.column_config.LinkColumn(
                "📄 Ver",
                help="Click para ver el documento",
                display_text="Abrir"
            )
        }
    )
else:
    st.info("No hay documentos con los filtros seleccionados.")

# Solo mostrar formularios de edición si el usuario puede editar
if can_edit():
    st.markdown("---")
    st.subheader("➕ Subir / ✏️ Editar / 🗑️ Eliminar")

    tab_upload, tab_edit, tab_delete = st.tabs(["Subir Documento", "Editar", "Eliminar"])

    with tab_upload:
        st.info("� Crear anexo sin archivo asociado")
        
        # Obtener personas para el selector
        personas = personas_service.listar(solo_activas=True)
        personas_opts = {p.nombre: p.id for p in personas}
        
        with st.form("form_upload", clear_on_submit=True):
            # Selector de proyecto
            proyecto_sel = st.selectbox("Proyecto *", list(proyecto_opts.keys()), key="upload_proyecto")
            proyecto_id_sel = proyecto_opts[proyecto_sel]
            
            # Descripción general
            descripcion = st.text_area("Descripción", placeholder="Descripción general del anexo", height=80)
            
            # Campos adicionales: valor, IVA, nombre y fecha
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                valor = st.number_input("Valor", min_value=0.0, value=0.0, step=0.01, format="%.2f",
                                       help="Valor numérico del anexo (acepta decimales)")
            with col_v2:
                iva = st.number_input("IVA", min_value=0.0, value=0.0, step=0.01, format="%.2f",
                                     help="Valor del IVA (acepta decimales)")
            
            col_n, col_f = st.columns(2)
            with col_n:
                # Selector de nombre de persona (autocompletable con searchbox)
                persona_sel = st.selectbox(
                    "Nombre de Persona",
                    options=list(personas_opts.keys()),
                    index=None,
                    placeholder="Escribe para buscar...",
                    help="Selecciona la persona asociada al anexo"
                )
                persona_id_sel = personas_opts.get(persona_sel) if persona_sel else None
            with col_f:
                fecha_documento = st.date_input("Fecha del documento", value=None,
                                               help="Fecha del documento (puede ser cualquier fecha)")
            
            # CAMPO DE CARGA DE ARCHIVOS OCULTO
            # uploaded_files = st.file_uploader(
            #     "Selecciona archivo(s)",
            #     accept_multiple_files=True,
            #     help="Puedes seleccionar múltiples archivos"
            # )
            
            if st.form_submit_button("� Crear Anexo"):
                try:
                    # Crear registro en BD sin archivo físico
                    nombre_archivo = f"Anexo_{proyecto_sel}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    if persona_sel:
                        nombre_archivo += f"_{persona_sel.replace(' ', '_')}"
                    
                    dto = DocumentoCreate(
                        proyecto_id=proyecto_id_sel,
                        nombre_archivo=nombre_archivo,
                        descripcion=descripcion.strip() if descripcion.strip() else None,
                        ruta_archivo=None,  # Sin archivo físico
                        tamanio_bytes=0,
                        tipo_mime=None,
                        valor=valor if valor > 0 else None,
                        iva=iva if iva > 0 else None,
                        fecha_documento=fecha_documento
                    )
                    documentos_service.crear(dto)
                    st.success("✅ Anexo creado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al crear anexo: {str(e)}")

    with tab_edit:
        if not items:
            st.info("No hay documentos para editar.")
        else:
            options = {f"{d.id} - {d.nombre_archivo} ({d.proyecto_nombre})": d for d in items}
            sel_key = st.selectbox("Selecciona documento", list(options.keys()), key="edit_select")
            sel = options[sel_key]
            
            with st.form("form_edit"):
                nombre_e = st.text_input("Nombre del archivo", sel.nombre_archivo)
                desc_e = st.text_area("Descripción", sel.descripcion or "", height=100)
                
                # Campos adicionales: valor y fecha
                col_ve, col_fe = st.columns(2)
                with col_ve:
                    valor_e = st.number_input("Valor", min_value=0.0, value=float(sel.valor or 0.0), step=0.01, format="%.2f",
                                             help="Valor numérico del anexo (acepta decimales)")
                    iva_e = st.number_input("IVA", min_value=0.0, value=float(sel.iva or 0.0), step=0.01, format="%.2f",
                                           help="Valor del IVA (acepta decimales)")
                with col_fe:
                    fecha_doc_e = st.date_input("Fecha del documento", value=sel.fecha_documento,
                                               help="Fecha del documento (puede ser cualquier fecha)")
                
                st.caption(f"📁 Ruta: {sel.ruta_archivo}")
                st.caption(f"📅 Subido: {sel.fecha_carga.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if st.form_submit_button("💾 Guardar cambios"):
                    try:
                        dto = DocumentoUpdate(
                            id=sel.id,
                            nombre_archivo=nombre_e.strip(),
                            descripcion=desc_e.strip() if desc_e.strip() else None,
                            valor=valor_e if valor_e > 0 else None,
                            iva=iva_e if iva_e > 0 else None,
                            fecha_documento=fecha_doc_e
                        )
                        documentos_service.actualizar(dto)
                        st.success("Cambios guardados")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    with tab_delete:
        st.warning("⚠️ **Advertencia**: Esta acción eliminará permanentemente el documento del servidor.")
        
        if not items:
            st.info("No hay documentos para eliminar.")
        else:
            # Filtro por proyecto para eliminar
            col_del1, col_del2 = st.columns([1, 2])
            with col_del1:
                proyecto_del_filter = st.selectbox("Filtrar por Proyecto", ["(Todos)"] + list(proyecto_opts.keys()), key="delete_proyecto_filter")
                proyecto_id_del = None if proyecto_del_filter == "(Todos)" else proyecto_opts[proyecto_del_filter]
            
            # Filtrar documentos por proyecto seleccionado
            items_del = [d for d in items if proyecto_id_del is None or d.proyecto_id == proyecto_id_del]
            
            if not items_del:
                st.info("No hay documentos en el proyecto seleccionado.")
            else:
                options_del = {f"{d.id} - {d.nombre_archivo} ({d.proyecto_nombre})": d for d in items_del}
                with col_del2:
                    sel_del = options_del[st.selectbox("Selecciona documento a eliminar", list(options_del.keys()), key="delete_select")]
            
                st.error(f"Vas a eliminar: **{sel_del.nombre_archivo}**")
                st.caption(f"Proyecto: {sel_del.proyecto_nombre}")
                st.caption(f"Subido: {sel_del.fecha_carga.strftime('%Y-%m-%d %H:%M:%S')}")
                
                confirmar = st.checkbox("Confirmo que deseo eliminar este documento", key="confirm_delete")
                
                if st.button("🗑️ Eliminar permanentemente", type="primary", disabled=not confirmar):
                    try:
                        documentos_service.eliminar(sel_del.id)
                        st.success(f"Documento '{sel_del.nombre_archivo}' eliminado exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar: {str(e)}")
