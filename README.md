# 🧮 Simulador de Finanzas Personales

Este proyecto es una aplicación fullstack para gestionar y visualizar tus finanzas personales.

# 🧮 Finance Simulator - Backend

Este es el backend del proyecto **Finance Simulator**, una aplicación web para gestionar finanzas personales. Proporciona una API REST construida con **Django REST Framework** y autenticación basada en **JWT**. La base de datos es **PostgreSQL**, desplegada en **Render**.

### 🚀 Enlace a producción

🔗 Backend API: [https://finance-backend-9v2i.onrender.com](https://finance-backend-9v2i.onrender.com)

---

## 📦 Tecnologías usadas

- Python 3.11
- Django 5
- Django REST Framework
- PostgreSQL
- JWT (SimpleJWT)
- Render (deployment)

---

## 📁 Estructura principal

- backend/
- ├── api/
- │ ├── models.py # Modelo de transacciones
- │ ├── serializers.py # Validaciones y representación de datos
- │ ├── views.py # APIView y ViewSet
- │ ├── filters.py # Filtros personalizados
- │ └── urls.py
- ├── backend/
- │ ├── settings.py
- │ └── urls.py
- └── manage.py

## 🛠️ Cómo ejecutar localmente

1. Clonar el repositorio y crear un entorno virtual:

   ```bash
   git clone https://github.com/tu-usuario/finance-simulator.git
   cd finance-simulator/backend
   python -m venv env
   source env/bin/activate  # o env\Scripts\activate en Windows

   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txts

   ```

3. Crear archivo .env con variables necesarias:

   ```ini
   DEBUG=true
   SECRET_KEY=tu_clave_secreta
   DB_NAME=finance_db
   DB_USER=postgres
   DB_PASSWORD=tu_password
   DB_HOST=localhost
   DB_PORT=5432

   ```

4. Aplicar migraciones y crear superusuario:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser

   ```

5. Ejecutar el servidor:

   ```bash
   python manage.py runserver

   ```

## 🧪 Endpoints disponibles

- POST /api/token/ – Obtener JWT
- POST /api/token/refresh/ – Refrescar JWT
- GET/POST /api/transactions/ – Ver o crear transacciones
- GET /api/transactions/?type=income – Filtrar por tipo
- GET /api/transactions/?min_amount=100&max_amount=500 – Rango de montos

# 💼 Finance Simulator - Frontend

Este es el frontend de la aplicación **Finance Simulator**, desarrollada en **React + TypeScript**. Se conecta con un backend en Django para permitir a los usuarios autenticarse y gestionar transacciones personales.

### 🌍 Enlace a producción

🔗 Frontend App: [https://finance-frontend-pink.vercel.app](https://finance-frontend-pink.vercel.app)

---

## 🧰 Tecnologías usadas

- React 19 (CRA)
- TypeScript
- TailwindCSS
- Chart.js
- Axios
- React Router DOM
- Vercel (deployment)

---

## 🌱 Variables de entorno

El frontend usa variables para conectarse con el backend. Configura `.env.development` o `.env.production`:

```env
REACT_APP_API_BASE_URL=https://finance-backend-9v2i.onrender.com/api
```

## 🚀 Cómo ejecutar localmente

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/finance-simulator.git
   cd finance-simulator/frontend

   ```

2. Instalar dependencias:

   ```bash
   npm install

   ```

3. Crear archivo .env.development:

   ```ini
   REACT_APP_API_BASE_URL=http://localhost:8000/api

   ```

4. Ejecutar app localmente:

   ```bash
   npm start

   ```

## 📁 Estructura

- frontend/
- ├── public/
- │ ├── index.html
- │ └── manifest.json
- ├── src/
- │ ├── services/
- │ │ └── apiClient.ts
- │ ├── pages/
- │ ├── components/
- │ └── App.tsx
- ├── .env.development
- └── tailwind.config.js

## 🧪 Funcionalidades

- Login de usuario con JWT
- Listado paginado de transacciones
- Creación de nuevas transacciones
- Filtros por tipo, monto y fecha
- Visualización de gráficos con Chart.js
