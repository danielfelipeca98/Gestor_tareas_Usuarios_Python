from fastapi import FastAPI,HTTPException
from modelsUsuario import UsuarioRegister,UsuarioLogin,UsuarioResponse,TokenResponse
from database import get_db
from passlib.context import CryptContext
from auth import crear_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

app = FastAPI()

@app.post("/register",response_model= UsuarioResponse, status_code=201)
def register_usuario(usuario: UsuarioRegister):
    conexion,cursor = get_db()

    cursor.execute("SELECT id FROM usuarios WHERE email =?",(usuario.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    password_hash = pwd_context.hash(usuario.password)

    cursor.execute("""
    INSERT INTO usuarios(nombre,email,password_hash)
    VALUES(?,?,?)
    """,(usuario.nombre, usuario.email,password_hash))
    
    conexion.commit()
    nuevo_id = cursor.lastrowid
        
    nueva = {
        "id":nuevo_id,
        "nombre":usuario.nombre,
        "email":usuario.email
        }

    return nueva

@app.post("/login",response_model=TokenResponse,status_code=200)
def login_usuarios(usuario:UsuarioLogin):
    conexion,cursor = get_db()

    cursor.execute("SELECT id, nombre, password_hash FROM usuarios WHERE email = ?",usuario.email)
    usuario_db = cursor.fetchone()
    if not  usuario_db:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    usuario_id = usuario_db[0]
    nombre = usuario_db[1]
    hash_guardado = usuario_db[2]

    if not pwd_context.verify(usuario.password,hash_guardado):
        raise HTTPException(status_code=401, detail="contraseña incorrecta")

    token = crear_token({"sub":str(usuario_id), "nombre": nombre})

    return TokenResponse(access_token=token, token_type="bearer")