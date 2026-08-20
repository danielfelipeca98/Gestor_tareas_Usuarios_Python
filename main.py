from fastapi import FastAPI, HTTPException, Depends
from models import TareaCreate, TareaUpdate, TareaResponse
from modelsUsuario import UsuarioRegister, UsuarioLogin, UsuarioResponse, TokenResponse
from database import get_db
from passlib.context import CryptContext
from auth import crear_token, get_current_user

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

app = FastAPI()

@app.post("/register", response_model=UsuarioResponse, status_code=201)
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

@app.post("/login", response_model=TokenResponse, status_code=200)
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

@app.get("/tareas", response_model=list[TareaResponse])
def listar_tareas(usuario: dict = Depends(get_current_user)):
    conexion, cursor = get_db()

    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tareas
        WHERE usuario_id = ?
    """, (usuario["id"],))
    
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

@app.get("/tareas/{tarea_id}", response_model=TareaResponse)
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

@app.post("/tareas", response_model=TareaResponse, status_code=201)
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

@app.put("/tareas/{tarea_id}", response_model=TareaResponse)
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

@app.delete("/tareas/{tarea_id}")
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