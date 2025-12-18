# apps/api/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import ORJSONResponse, FileResponse
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
    documentos_service
)
from domain.schemas.personas import PersonaListItem
from domain.schemas.proyectos import ProyectoListItem
from domain.schemas.sprints import SprintListItem
from domain.schemas.asignaciones import AsignacionListItem
from domain.schemas.usuarios import UsuarioListItem

app = FastAPI(
    title="Project Ops API - Read Only",
    description="API REST de solo lectura para consulta de proyectos, sprints, personas y asignaciones. No permite crear, editar ni eliminar datos.",
    version="1.0.0",
    default_response_class=ORJSONResponse
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

# ==================== USUARIOS ====================
@app.get("/api/usuarios", response_model=List[UsuarioListItem], tags=["Usuarios"])
def listar_usuarios(
    current_user: dict = Depends(get_current_user)
):
    """Obtener lista de usuarios (solo para admins)"""
    if current_user.get("rol_app", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para ver usuarios")
    return usuarios_service.listar()

# ==================== HEALTH CHECK ====================
@app.get("/api/health", tags=["Health"])
def health_check():
    """Verificar estado de la API"""
    return {"status": "ok", "service": "Project Ops API"}

# ==================== DOCUMENTOS ====================
@app.get("/api/documentos/{documento_id}/download", tags=["Documentos"])
def descargar_documento(documento_id: int):
    """Descargar un documento por ID"""
    doc = documentos_service.obtener(documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if not os.path.exists(doc.ruta_archivo):
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
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if not os.path.exists(doc.ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")
    
    # Para visualización inline en el navegador
    return FileResponse(
        path=doc.ruta_archivo,
        filename=doc.nombre_archivo,
        media_type=doc.tipo_mime or "application/octet-stream",
        headers={"Content-Disposition": f"inline; filename=\"{doc.nombre_archivo}\""}
    )

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
            "personas": "/api/personas",
            "proyectos": "/api/proyectos",
            "sprints": "/api/sprints",
            "asignaciones": "/api/asignaciones",
            "usuarios": "/api/usuarios"
        }
    }
