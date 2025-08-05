from django.urls import path
from .views import register_user, create_demo_user, create_superuser, run_migrations

urlpatterns = [
    path('auth/register/', register_user, name='register'),
    path('auth/demo/', create_demo_user, name='demo'),
    path('setup/create-superuser/', create_superuser, name='create-superuser'),
	path('setup/run-migrations/', run_migrations, name='run-migrations'),
]

"""
ENDPOINTS

============= 🛠️ UTILIDADES SETUP =============
POST   /api/setup/run-migrations/          -> Ejecutar migraciones
POST   /api/setup/create-superuser/        -> Crear superusuario

============= 🔐 AUTENTICACIÓN =============
POST   /api/auth/register/                 -> Registro de usuario
POST   /api/auth/demo/                     -> Crear usuario demo

"""