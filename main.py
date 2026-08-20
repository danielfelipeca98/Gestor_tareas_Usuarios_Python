from fastapi import FastAPI, HTTPException, Depends, Query, status
from typing import Optional, List
from models import TareaCreate, TareaUpdate, TareaResponse
from modelsUsuario import UsuarioRegister, UsuarioLogin, UsuarioResponse, TokenResponse
from database import get_db
from passlib.context import CryptContext
from auth import crear_token, get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(
    title="API de Gestión de Tareas",
    description="""
    ## API para gestionar tareas con autenticación JWT

    ### Características:
    - Registro y autenticación de usuarios
    - CRUD completo de tareas
    - Cada tarea asociada a un usuario
    - Documentación interactiva con Swagger

    ### Flujo básico:
    1. Registrarse en `/register`
    2. Login en `/login` para obtener el token JWT
    3. Usar el token en el header `Authorization: Bearer <token>`
    4. Gestionar tareas con los endpoints protegidos
    """,
    version="2.0.0",
    contact={
        "name": "Tu Nombre",
        "email": "tu@email.com",
        "url": "https://github.com/tu-usuario",
    },
    
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario con nombre, email y contraseña.",
    tags=["Autenticación"],
    responses={
        201: {"description": "Usuario registrado exitosamente"},
        400: {"description": "Email ya registrado o datos inválidos"},
        422: {"description": "Error de validación de datos"}
    }
)
def register_usuario(usuario: UsuarioRegister):
    conexion, cursor = get_db()

    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (usuario.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    password_hash = pwd_context.hash(usuario.password)

    cursor.execute("""
        INSERT INTO usuarios (nombre, email, password_hash)
        VALUES (?, ?, ?)
    """, (usuario.nombre, usuario.email, password_hash))
    
    conexion.commit()
    nuevo_id = cursor.lastrowid
        
    return {
        "id": nuevo_id,
        "nombre": usuario.nombre,
        "email": usuario.email
    }


@app.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Autentica a un usuario y devuelve un token JWT.",
    tags=["Autenticación"],
    responses={
        200: {"description": "Login exitoso, devuelve token JWT"},
        400: {"description": "Usuario no encontrado"},
        401: {"description": "Contraseña incorrecta"}
    }
)
def login_usuarios(usuario: UsuarioLogin):
    conexion, cursor = get_db()

    cursor.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = ?", (usuario.email,))
    usuario_db = cursor.fetchone()
    
    if not usuario_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    usuario_id = usuario_db[0]
    nombre = usuario_db[1]
    hash_guardado = usuario_db[2]

    if not pwd_context.verify(usuario.password, hash_guardado):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token({"sub": str(usuario_id), "nombre": nombre})

    return {"access_token": token, "token_type": "bearer"}


@app.get(
    "/tareas",
    response_model=List[TareaResponse],
    summary="Listar todas las tareas",
    description="Obtiene todas las tareas del usuario autenticado.",
    tags=["Tareas"],
    responses={
        200: {"description": "Lista de tareas obtenida exitosamente"},
        401: {"description": "Token inválido o no proporcionado"}
    }
)
def listar_tareas(
    estado: Optional[str] = Query(
        None,
        description="Filtrar por estado de la tarea",
        examples=["pendiente", "en progreso", "completada", "cancelada"]
    ),
    limite: int = Query(
        10,
        description="Número máximo de resultados a devolver",
        ge=1,
        le=100,
        example=10
    ),
    offset: int = Query(
        0,
        description="Número de resultados a saltar (para paginación)",
        ge=0,
        example=0
    ),
    usuario: dict = Depends(get_current_user)
):
    conexion, cursor = get_db()

    query = """
        SELECT id, titulo, descripcion, estado
        FROM tareas
        WHERE usuario_id = ?
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (usuario["id"], limite, offset))
    
    filas = cursor.fetchall()
    
    return [
        {
            "id": f[0],
            "titulo": f[1],
            "descripcion": f[2],
            "estado": f[3]
        }
        for f in filas
    ]


@app.get(
    "/tareas/{tarea_id}",
    response_model=TareaResponse,
    summary="Obtener una tarea por ID",
    description="Obtiene los detalles de una tarea específica.",
    tags=["Tareas"],
    responses={
        200: {"description": "Tarea obtenida exitosamente"},
        401: {"description": "Token inválido o no proporcionado"},
        404: {"description": "Tarea no encontrada o no te pertenece"}
    }
)
def mostrar_tarea(
    tarea_id: int,
    usuario: dict = Depends(get_current_user)
):
    conexion, cursor = get_db()

    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tareas
        WHERE id = ? AND usuario_id = ?
    """, (tarea_id, usuario["id"]))
    
    fila = cursor.fetchone()

    if not fila:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no te pertenece")

    return {
        "id": fila[0],
        "titulo": fila[1],
        "descripcion": fila[2],
        "estado": fila[3]
    }


@app.post(
    "/tareas",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva tarea",
    description="Crea una nueva tarea asociada al usuario autenticado.",
    tags=["Tareas"],
    responses={
        201: {"description": "Tarea creada exitosamente"},
        401: {"description": "Token inválido o no proporcionado"},
        422: {"description": "Error de validación de datos"}
    }
)
def crear_tarea(
    tarea: TareaCreate,
    usuario: dict = Depends(get_current_user)
):
    conexion, cursor = get_db()

    cursor.execute("SELECT id, nombre FROM usuarios WHERE id = ?", (usuario["id"],))
    tarea_db = cursor.fetchone()
    
    if not tarea_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cursor.execute("""
        INSERT INTO tareas (titulo, descripcion, estado, usuario_id)
        VALUES (?, ?, ?, ?)
    """, (tarea.titulo, tarea.descripcion, tarea.estado, usuario["id"]))

    conexion.commit()
    nuevo_id = cursor.lastrowid
    
    return {
        "id": nuevo_id,
        "titulo": tarea.titulo,
        "descripcion": tarea.descripcion,
        "estado": tarea.estado
    }


@app.put(
    "/tareas/{tarea_id}",
    response_model=TareaResponse,
    summary="Actualizar una tarea",
    description="Actualiza los campos de una tarea existente.",
    tags=["Tareas"],
    responses={
        200: {"description": "Tarea actualizada exitosamente"},
        401: {"description": "Token inválido o no proporcionado"},
        404: {"description": "Tarea no encontrada o no te pertenece"}
    }
)
def actualizar_tarea(
    tarea_id: int,
    tarea: TareaUpdate,
    usuario: dict = Depends(get_current_user)
):
    conexion, cursor = get_db()

    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tareas
        WHERE id = ? AND usuario_id = ?
    """, (tarea_id, usuario["id"]))
    
    fila = cursor.fetchone()
    
    if not fila:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no te pertenece")
    
    updates = []
    values = []
    
    if tarea.titulo is not None:
        updates.append("titulo = ?")
        values.append(tarea.titulo)
    if tarea.descripcion is not None:
        updates.append("descripcion = ?")
        values.append(tarea.descripcion)
    if tarea.estado is not None:
        updates.append("estado = ?")
        values.append(tarea.estado)
    
    if updates:
        values.append(tarea_id)
        query = f"UPDATE tareas SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conexion.commit()
    
    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tareas
        WHERE id = ?
    """, (tarea_id,))
    
    fila = cursor.fetchone()
    
    return {
        "id": fila[0],
        "titulo": fila[1],
        "descripcion": fila[2],
        "estado": fila[3]
    }


@app.delete(
    "/tareas/{tarea_id}",
    summary="Eliminar una tarea",
    description="Elimina una tarea existente del usuario autenticado.",
    tags=["Tareas"],
    responses={
        200: {"description": "Tarea eliminada exitosamente"},
        401: {"description": "Token inválido o no proporcionado"},
        404: {"description": "Tarea no encontrada o no te pertenece"}
    }
)
def eliminar_tarea(
    tarea_id: int,
    usuario: dict = Depends(get_current_user)
):
    conexion, cursor = get_db()
    
    cursor.execute("""
        SELECT titulo
        FROM tareas
        WHERE id = ? AND usuario_id = ?
    """, (tarea_id, usuario["id"]))
    
    fila = cursor.fetchone()
    
    if not fila:
        raise HTTPException(status_code=404, detail="Tarea no encontrada o no te pertenece")
    
    titulo = fila[0]
    
    cursor.execute("DELETE FROM tareas WHERE id = ? AND usuario_id = ?", (tarea_id, usuario["id"]))
    conexion.commit()
    
    return {"mensaje": f"Tarea '{titulo}' eliminada"}