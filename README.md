#  API de Tareas con FastAPI

API REST para gestión de tareas con autenticación JWT y SQLite.

##  Características

-  Autenticación JWT
-  Registro y login de usuarios
-  CRUD de tareas
-  Tareas asociadas a usuarios
-  Documentación Swagger automática
-  Persistencia en SQLite

##  Tecnologías

- **FastAPI** → API REST
- **JWT** → Autenticación
- **SQLite** → Base de datos
- **Passlib** → Encriptación de contraseñas
- **Pydantic** → Validación de datos

##  Estructura del proyecto

```
proyectoTareas/
├── main.py              # Endpoints
├── auth.py              # JWT y autenticación
├── database.py          # Conexión SQLite
├── models.py            # Modelos Pydantic (tareas)
├── modelsUsuario.py     # Modelos Pydantic (usuarios)
├── configAuth.py        # Configuración JWT
├── requirements.txt     # Dependencias
├── .gitignore           # Archivos ignorados
└── README.md            # Documentación
```

##  Cómo ejecutar

```bash
# 1. Clonar
git clone https://github.com/TU-USUARIO/api-tareas-fastapi.git
cd api-tareas-fastapi

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
uvicorn main:app --reload
```

##  Endpoints

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| POST | `/register` | Registrar usuario |  No |
| POST | `/login` | Login (devuelve JWT) |  No |
| GET | `/tareas` | Listar tareas |  Sí |
| POST | `/tareas` | Crear tarea |  Sí |
| GET | `/tareas/{id}` | Obtener tarea |  Sí |
| PUT | `/tareas/{id}` | Actualizar tarea |  Sí |
| DELETE | `/tareas/{id}` | Eliminar tarea |  Sí |

##  Autor

**Daniel Felipe Castro**
- [GitHub]https://github.com/danielfelipeca98