from django.urls import path
from .views import (
    register_user, create_demo_user, create_superuser, 
    run_migrations, user_profile
)

urlpatterns = [
    # Autenticación
    path('auth/register/', register_user, name='register'),
    path('auth/demo/', create_demo_user, name='demo'),
    path('auth/profile/', user_profile, name='user-profile'),
    
    # Setup/Utilidades
    path('setup/create-superuser/', create_superuser, name='create-superuser'),
    path('setup/run-migrations/', run_migrations, name='run-migrations'),
]

"""
ENDPOINTS ACTUALIZADOS

============= 🛠️ UTILIDADES SETUP =============
POST   /api/setup/run-migrations/          -> Ejecutar migraciones
POST   /api/setup/create-superuser/        -> Crear superusuario

============= 🔐 AUTENTICACIÓN =============
POST   /api/auth/register/                 -> Registro de usuario
POST   /api/auth/demo/                     -> Crear usuario demo
GET    /api/auth/profile/                  -> Obtener perfil del usuario

============= 🔑 JWT TOKENS =============
POST   /api/token/                         -> Obtener tokens (login)
POST   /api/token/refresh/                 -> Refrescar token
"""