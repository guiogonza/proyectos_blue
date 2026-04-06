# apps/api/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import ORJSONResponse, FileResponse, HTMLResponse
from typing import List, Optional
import sys
import os

# Agregar path raíz al PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from domain.services import (
    personas_service,
    proyectos_service,
    sprints_service,
    asignaciones_service,
    usuarios_service,
    auth_service,
    documentos_service,
    perfiles_service
)
from domain.schemas.personas import PersonaListItem
from domain.schemas.proyectos import ProyectoListItem
from domain.schemas.sprints import SprintListItem
from domain.schemas.asignaciones import AsignacionListItem
from domain.schemas.usuarios import UsuarioListItem
from domain.schemas.documentos import DocumentoListItem
from domain.schemas.perfiles import PerfilListItem

tags_metadata = [
    {"name": "Anexos", "description": "Consulta de anexos/documentos asociados a proyectos"},
    {"name": "Asignaciones", "description": "Consulta de asignaciones persona-proyecto"},
    {"name": "Documentos", "description": "Ver y descargar archivos de documentos"},
    {"name": "Health", "description": "Estado de la API"},
    {"name": "Perfiles", "description": "Consulta de perfiles y tarifas"},
    {"name": "Personas", "description": "Consulta de personas"},
    {"name": "Proyectos", "description": "Consulta de proyectos"},
    {"name": "Sprints", "description": "Consulta de sprints"},
    {"name": "Usuarios", "description": "Consulta de usuarios"},
]

app = FastAPI(
    title="Project Ops API - Read Only",
    description="API REST de solo lectura para consulta de proyectos, sprints, personas y asignaciones. No permite crear, editar ni eliminar datos.",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    openapi_tags=tags_metadata,
    root_path=os.getenv("API_ROOT_PATH", ""),
)

# Configurar CORS para permitir acceso desde cualquier origen
# Solo permite métodos GET (read-only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],  # Solo lectura
    allow_headers=["*"],
)

security = HTTPBasic()

# Autenticación básica
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = auth_service.verify_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

# ==================== ANEXOS (DOCUMENTOS) ====================
@app.get("/api/anexos", response_model=List[DocumentoListItem], tags=["Anexos"])
def listar_anexos(
    proyecto_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener lista de anexos/documentos.
    - proyecto_id: Filtrar por proyecto específico
    - search: Buscar por nombre o descripción
    
    Retorna información completa de cada anexo incluyendo URLs para ver/descargar.
    """
    items = documentos_service.listar(proyecto_id=proyecto_id, search=search)
    return items

@app.get("/api/anexos/proyecto/{proyecto_id}", tags=["Anexos"])
def listar_anexos_por_proyecto(
    proyecto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener todos los anexos de un proyecto específico con URLs de acceso.
    Retorna la información de la tabla y links para ver cada documento.
    """
    items = documentos_service.listar(proyecto_id=proyecto_id)
    
    # Construir respuesta con URLs de acceso
    result = []
    for doc in items:
        doc_dict = doc.dict()
        doc_dict["url_ver"] = f"/api/documentos/{doc.id}/view"
        doc_dict["url_descargar"] = f"/api/documentos/{doc.id}/download"
        result.append(doc_dict)
    
    return {
        "proyecto_id": proyecto_id,
        "total_anexos": len(result),
        "anexos": result
    }

@app.get("/api/anexos/{anexo_id}", response_model=DocumentoListItem, tags=["Anexos"])
def obtener_anexo(
    anexo_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener un anexo por ID"""
    doc = documentos_service.obtener(anexo_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    return doc

# ==================== ASIGNACIONES ====================
@app.get("/api/asignaciones", response_model=List[AsignacionListItem], tags=["Asignaciones"])
def listar_asignaciones(
    persona_id: Optional[int] = None,
    proyecto_id: Optional[int] = None,
    solo_activas: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de asignaciones"""
    return asignaciones_service.listar(persona_id, proyecto_id, solo_activas)

@app.get("/api/asignaciones/{asignacion_id}", response_model=AsignacionListItem, tags=["Asignaciones"])
def obtener_asignacion(
    asignacion_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener una asignación por ID"""
    asignaciones = asignaciones_service.listar()
    asignacion = next((a for a in asignaciones if a.id == asignacion_id), None)
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return asignacion

# ==================== DOCUMENTOS ====================
@app.get("/api/documentos/{documento_id}/download", tags=["Documentos"])
def descargar_documento(documento_id: int):
    """Descargar un documento por ID"""
    doc = documentos_service.obtener(documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if not doc.ruta_archivo or not os.path.exists(doc.ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")
    
    return FileResponse(
        path=doc.ruta_archivo,
        filename=doc.nombre_archivo,
        media_type=doc.tipo_mime or "application/octet-stream"
    )

@app.get("/api/documentos/{documento_id}/view", tags=["Documentos"])
def ver_documento(documento_id: int):
    """Ver un documento en el navegador (inline)"""
    doc = documentos_service.obtener(documento_id)
    if not doc:
        return HTMLResponse(
            content="""
            <html><head><title>No encontrado</title>
            <style>body{font-family:Arial,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#1a1a2e;color:#e0e0e0;}
            .box{text-align:center;padding:40px;border-radius:12px;background:#16213e;box-shadow:0 4px 20px rgba(0,0,0,0.3);}
            h1{color:#e94560;font-size:48px;margin:0 0 10px;} p{font-size:18px;color:#a0a0b0;}
            a{color:#fff;background:#e94560;padding:10px 24px;border-radius:6px;text-decoration:none;display:inline-block;margin-top:20px;}
            </style></head><body><div class='box'><h1>404</h1><p>Documento no encontrado</p><a href='javascript:window.close()'>Cerrar</a></div></body></html>
            """,
            status_code=404
        )
    
    tiene_archivo = doc.ruta_archivo and os.path.exists(doc.ruta_archivo)
    
    # Formatear valores
    valor_fmt = f"${doc.valor:,.2f}" if doc.valor else "N/A"
    iva_fmt = f"${doc.iva:,.2f}" if doc.iva else "N/A"
    fecha_doc_fmt = doc.fecha_documento.strftime("%Y-%m-%d") if doc.fecha_documento else "N/A"
    fecha_carga_fmt = doc.fecha_carga.strftime("%Y-%m-%d %H:%M:%S") if doc.fecha_carga else "N/A"
    descripcion = doc.descripcion or "N/A"
    proyecto = doc.proyecto_nombre or f"Proyecto ID {doc.proyecto_id}"
    
    # Botón de descarga solo si hay archivo
    download_btn = ""
    if tiene_archivo:
        download_btn = f'<a href="/api/documentos/{doc.id}/download" class="btn btn-download">⬇ Descargar archivo</a>'
    
    # Si tiene archivo físico, mostrar visor con iframe + info
    if tiene_archivo:
        archivo_section = f'''
        <div class="file-viewer">
            <iframe src="/api/documentos/{doc.id}/download" width="100%" height="500px" style="border:none;border-radius:8px;"></iframe>
        </div>'''
    else:
        archivo_section = '''
        <div class="no-file">
            <span class="no-file-icon">📋</span>
            <p>Este anexo es un registro de datos sin archivo físico adjunto</p>
        </div>'''
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{doc.nombre_archivo}</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#0e1117; color:#e0e0e0; min-height:100vh; padding:20px; }}
            .container {{ max-width:900px; margin:0 auto; }}
            .header {{ background:linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); padding:24px 30px; border-radius:12px 12px 0 0; border-bottom:2px solid #e94560; }}
            .header h1 {{ font-size:18px; color:#fff; word-break:break-all; }}
            .header .subtitle {{ color:#a0a0b0; font-size:13px; margin-top:6px; }}
            .body {{ background:#16213e; padding:24px 30px; }}
            .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
            .card {{ background:#0f3460; border-radius:8px; padding:16px; }}
            .card .label {{ font-size:11px; text-transform:uppercase; color:#7a8ba0; letter-spacing:1px; margin-bottom:4px; }}
            .card .value {{ font-size:18px; font-weight:600; color:#fff; }}
            .card .value.money {{ color:#4ecca3; }}
            .card .value.desc {{ font-size:14px; font-weight:normal; color:#c0c0d0; }}
            .file-viewer {{ margin-top:20px; }}
            .no-file {{ text-align:center; padding:40px 20px; background:#0f3460; border-radius:8px; margin-top:20px; }}
            .no-file-icon {{ font-size:48px; display:block; margin-bottom:10px; }}
            .no-file p {{ color:#7a8ba0; font-size:14px; }}
            .footer {{ background:#16213e; padding:20px 30px; border-radius:0 0 12px 12px; display:flex; gap:12px; justify-content:flex-end; border-top:1px solid #0f3460; }}
            .btn {{ padding:10px 24px; border-radius:6px; text-decoration:none; font-size:14px; font-weight:500; display:inline-flex; align-items:center; gap:6px; cursor:pointer; border:none; }}
            .btn-download {{ background:#4ecca3; color:#0e1117; }}
            .btn-download:hover {{ background:#3db88f; }}
            .btn-close {{ background:#374151; color:#e0e0e0; }}
            .btn-close:hover {{ background:#4b5563; }}
            @media (max-width:600px) {{ .grid {{ grid-template-columns:1fr; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📄 {doc.nombre_archivo}</h1>
                <div class="subtitle">{proyecto} &middot; ID #{doc.id}</div>
            </div>
            <div class="body">
                <div class="grid">
                    <div class="card">
                        <div class="label">Valor</div>
                        <div class="value money">{valor_fmt}</div>
                    </div>
                    <div class="card">
                        <div class="label">IVA</div>
                        <div class="value money">{iva_fmt}</div>
                    </div>
                    <div class="card">
                        <div class="label">Descripción</div>
                        <div class="value desc">{descripcion}</div>
                    </div>
                    <div class="card">
                        <div class="label">Fecha Documento</div>
                        <div class="value">{fecha_doc_fmt}</div>
                    </div>
                </div>
                {archivo_section}
            </div>
            <div class="footer">
                {download_btn}
                <a href="javascript:window.close()" class="btn btn-close">✕ Cerrar</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)

# ==================== HEALTH CHECK ====================
@app.get("/api/health", tags=["Health"])
def health_check():
    """Verificar estado de la API"""
    return {"status": "ok", "service": "Project Ops API"}

# ==================== PERFILES ====================
@app.get("/api/perfiles", response_model=List[PerfilListItem], tags=["Perfiles"])
def listar_perfiles(
    solo_activos: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de perfiles"""
    return perfiles_service.listar(solo_activos, search)

@app.get("/api/perfiles/{perfil_id}", response_model=PerfilListItem, tags=["Perfiles"])
def obtener_perfil(
    perfil_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener un perfil por ID"""
    perfil = perfiles_service.obtener(perfil_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil

# ==================== PERSONAS ====================
@app.get("/api/personas", response_model=List[PersonaListItem], tags=["Personas"])
def listar_personas(
    search: Optional[str] = None,
    activo: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de personas"""
    return personas_service.listar(search, activo)

@app.get("/api/personas/{persona_id}", response_model=PersonaListItem, tags=["Personas"])
def obtener_persona(
    persona_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener una persona por ID"""
    personas = personas_service.listar()
    persona = next((p for p in personas if p.id == persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona

# ==================== PROYECTOS ====================
@app.get("/api/proyectos", response_model=List[ProyectoListItem], tags=["Proyectos"])
def listar_proyectos(
    search: Optional[str] = None,
    estado: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de proyectos"""
    return proyectos_service.listar(search, estado)

@app.get("/api/proyectos/{proyecto_id}", response_model=ProyectoListItem, tags=["Proyectos"])
def obtener_proyecto(
    proyecto_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener un proyecto por ID"""
    proyectos = proyectos_service.listar()
    proyecto = next((p for p in proyectos if p.id == proyecto_id), None)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto

# ==================== SPRINTS ====================
@app.get("/api/sprints", response_model=List[SprintListItem], tags=["Sprints"])
def listar_sprints(
    proyecto_id: Optional[int] = None,
    estado: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de sprints"""
    return sprints_service.listar(proyecto_id, estado, search)

@app.get("/api/sprints/{sprint_id}", response_model=SprintListItem, tags=["Sprints"])
def obtener_sprint(
    sprint_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Obtener un sprint por ID"""
    sprints = sprints_service.listar()
    sprint = next((s for s in sprints if s.id == sprint_id), None)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint no encontrado")
    return sprint

# ==================== USUARIOS ====================
@app.get("/api/usuarios", response_model=List[UsuarioListItem], tags=["Usuarios"])
def listar_usuarios(
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de usuarios (solo para admins)"""
    if current_user.get("rol_app", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para ver usuarios")
    return usuarios_service.listar()

@app.get("/", tags=["Root"])
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Project Ops API - Read Only",
        "version": "1.0.0",
        "mode": "read-only",
        "description": "API de solo consulta. No permite crear, editar ni eliminar datos.",
        "docs": "/docs",
        "endpoints": {
            "anexos": "/api/anexos",
            "anexos_por_proyecto": "/api/anexos/proyecto/{proyecto_id}",
            "asignaciones": "/api/asignaciones",
            "perfiles": "/api/perfiles",
            "personas": "/api/personas",
            "proyectos": "/api/proyectos",
            "sprints": "/api/sprints",
            "usuarios": "/api/usuarios"
        }
    }
