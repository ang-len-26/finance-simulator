# 🧮 Simulador de Finanzas Personales

Este proyecto es una aplicación fullstack para gestionar y visualizar tus finanzas personales.

## 🧱 Tecnologías utilizadas

### 🔙 Backend (Django + Django REST)

- Django 4.x
- Django REST Framework
- JWT Authentication
- PostgreSQL (opcional: SQLite por defecto)

### 🔝 Frontend (React + TypeScript)

- React 18
- TypeScript
- TailwindCSS
- Axios
- Context API

---

## 🚀 Estructura del Proyecto

- Finance-Simulator/
- │
- ├── backend/ # Proyecto Django
- │ └── api/ # App principal con modelo Transaction
- ├── frontend/ # Proyecto React
- │ └── src/ # Código fuente del frontend
- ├── venv/ # Entorno virtual (ignorado por Git)
- └── README.md

---

## 🛠️ Instalación

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

### Frontend

cd frontend
npm install
npm run dev

🔐 Acceso
El sistema usa autenticación JWT. Al iniciar sesión, el token se guarda en sessionStorage para autenticar futuras peticiones al backend.

📊 Funcionalidades
Registro e inicio de sesión con JWT

Visualización de transacciones financieras (ingresos, egresos, etc.)

Contextos globales para autenticación y finanzas

Estilo limpio y responsivo con TailwindCSS

Estructura modular y mantenible

✅ Pendientes/Futuras mejoras
Paginación de transacciones

CRUD completo (crear, editar, eliminar transacciones)

Filtros por tipo/fecha

Gráficas y reportes

Validaciones y mejoras de seguridad
```
