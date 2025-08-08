# 🚀 FinTrack Backend - Sistema de Finanzas Personales

> **Stack:** Django 5.2 + DRF + PostgreSQL + JWT  
> **Arquitectura:** Modular y escalable

## 📋 Índice

- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [🔧 Configuración Inicial](#-configuración-inicial)
- [📦 Módulos del Sistema](#-módulos-del-sistema)
- [⚡ Comandos Principales](#-comandos-principales)
- [🔑 Autenticación y Usuarios](#-autenticación-y-usuarios)
- [📊 API Endpoints](#-api-endpoints)
- [🗃️ Base de Datos](#️-base-de-datos)
- [🧪 Testing](#-testing)
- [📚 Documentación Adicional](#-documentación-adicional)

## 🏗️ Arquitectura del Sistema

### **Estructura Modular**

```
backend/
├── api/                          # Aplicaciones modulares
│   ├── core/                     # 👤 Base del sistema (usuarios, auth)
│   ├── accounts/                 # 🏦 Sistema de cuentas bancarias
│   ├── transactions/             # 💰 Transacciones y categorías
│   ├── analytics/                # 📊 Reportes y métricas
│   └── goals/                    # 🎯 Metas financieras
├── backend/                      # ⚙️ Configuración Django
├── media/                        # 📁 Archivos de usuario
├── static/                       # 🎨 Archivos estáticos
└── requirements.txt              # 📋 Dependencias
```

### **Principios de Diseño**

- ✅ **Modularidad**: Cada funcionalidad en su propia app
- ✅ **Escalabilidad**: Fácil agregar nuevos módulos
- ✅ **Mantenibilidad**: Código organizado y documentado
- ✅ **Testing**: Estructura preparada para pruebas

## 🔧 Configuración Inicial

### **Requisitos Previos**

- Python 3.9+
- PostgreSQL 13+
- pip y virtualenv

### **Instalación Rápida**

```bash
# 1. Clonar y navegar
git clone <repo-url>
cd finance-simulator/backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Configurar base de datos
python manage.py makemigrations core accounts transactions analytics goals
python manage.py migrate

# 6. Configuración automática completa
python manage.py setup_all
```

### **Variables de Entorno (.env)**

```bash
# Base de Datos PostgreSQL
DB_NAME=findtrackdb
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=tu_secret_key_muy_segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=tu_jwt_secret_key
```

## 📦 Módulos del Sistema

### **🏗️ Core** (`api/core/`)

**Base del sistema de usuarios y autenticación**

- **Modelos**: `UserProfile`
- **Funcionalidad**: Registro, login, perfiles de usuario
- **Comandos**: `setup_users`, `setup_demo`

### **🏦 Accounts** (`api/accounts/`)

**Sistema de cuentas bancarias**

- **Modelos**: `Account`
- **Funcionalidad**: Cuentas corrientes, ahorros, inversiones, crédito
- **Comandos**: `setup_demo_accounts`

### **💰 Transactions** (`api/transactions/`)

**Transacciones y categorización**

- **Modelos**: `Transaction`, `Category`
- **Funcionalidad**: Ingresos, gastos, transferencias, categorización
- **Comandos**: `setup_categories`, `setup_demo_transactions`

### **📊 Analytics** (`api/analytics/`)

**Reportes y análisis financiero**

- **Modelos**: `FinancialMetric`, `CategorySummary`, `BudgetAlert`
- **Funcionalidad**: Métricas, reportes, alertas de presupuesto
- **Comandos**: `setup_analytics`, `generate_metrics`

### **🎯 Goals** (`api/goals/`)

**Metas financieras y planificación**

- **Modelos**: `FinancialGoal`, `GoalContribution`, `GoalMilestone`, `GoalTemplate`
- **Funcionalidad**: Metas de ahorro, seguimiento de progreso
- **Comandos**: `setup_goal_templates`, `setup_demo_goals`

## ⚡ Comandos Principales

### **🚀 Configuración Automática**

```bash
# Configuración completa del sistema
python manage.py setup_all

# Configuración rápida (sin datos demo extensos)
python manage.py setup_all --quick

# Solo configuración base (sin usuario demo)
python manage.py setup_all --skip-demo

# Reset completo y reconfiguración
python manage.py setup_all --reset
```

### **🗃️ Base de Datos**

```bash
# Crear migraciones
python manage.py makemigrations [app_name]

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations

# Shell interactivo de Django
python manage.py shell
```

### **👤 Gestión de Usuarios**

```bash
# Crear superusuario personalizado
python manage.py setup_users

# Crear usuario demo con datos
python manage.py setup_demo
```

### **🎯 Datos de Ejemplo**

```bash
# Categorías predeterminadas
python manage.py setup_categories

# Plantillas de metas
python manage.py setup_goal_templates

# Cuentas demo
python manage.py setup_demo_accounts

# Transacciones demo
python manage.py setup_demo_transactions

# Metas demo
python manage.py setup_demo_goals
```

## 🔑 Autenticación y Usuarios

### **Credenciales por Defecto**

#### **👨‍💼 Administrador**

- **URL**: `http://localhost:8000/admin/`
- **Usuario**: `AngelAdminFindTrack`
- **Contraseña**: `@FindTrack2025`

#### **🎭 Usuario Demo**

- **Usuario**: `demo`
- **Contraseña**: `demo123`
- **Datos**: Cuentas, transacciones y metas precargadas

### **Autenticación JWT**

```bash
# Endpoint de login
POST /api/core/login/
{
    "username": "demo",
    "password": "demo123"
}

# Respuesta
{
    "access": "jwt_token_aqui",
    "refresh": "refresh_token_aqui",
    "user": {...}
}
```

## 📊 API Endpoints

### **Base URL**: `http://localhost:8000/api/`

#### **🏗️ Core**

- `POST /core/register/` - Registro de usuarios
- `POST /core/login/` - Login con JWT
- `GET /core/profile/` - Perfil del usuario

#### **🏦 Accounts**

- `GET /accounts/` - Listar cuentas
- `POST /accounts/` - Crear cuenta
- `GET /accounts/{id}/` - Detalle de cuenta
- `PUT /accounts/{id}/` - Actualizar cuenta

#### **💰 Transactions**

- `GET /transactions/` - Listar transacciones (con filtros)
- `POST /transactions/` - Crear transacción
- `GET /transactions/categories/` - Listar categorías

#### **📊 Analytics**

- `GET /analytics/reports/` - Reportes financieros
- `GET /analytics/metrics/` - Métricas precalculadas
- `GET /analytics/alerts/` - Alertas de presupuesto

#### **🎯 Goals**

- `GET /goals/` - Listar metas financieras
- `POST /goals/` - Crear meta
- `POST /goals/{id}/contribute/` - Contribuir a meta

### **Filtros Avanzados**

```bash
# Transacciones por fecha y tipo
GET /api/transactions/?date_from=2025-01-01&date_to=2025-12-31&type=expense

# Transacciones por categoría
GET /api/transactions/?category=alimentacion&account=1

# Reportes por período
GET /api/analytics/reports/?period=monthly&year=2025
```

## 🗃️ Base de Datos

### **Estructura de Tablas Principales**

```sql
-- Usuarios y perfiles
core_userprofile
auth_user

-- Sistema financiero
accounts_account
transactions_transaction
transactions_category

-- Analytics
analytics_financialmetric
analytics_categorysummary
analytics_budgetalert

-- Metas
goals_financialgoal
goals_goalcontribution
goals_goalmilestone
goals_goaltemplate
```

### **Comandos SQL Útiles**

```sql
-- Ver todas las tablas
\dt

-- Ver transacciones recientes
SELECT * FROM transactions_transaction ORDER BY date DESC LIMIT 10;

-- Ver balance total por usuario
SELECT user_id, SUM(balance) FROM accounts_account GROUP BY user_id;

-- Ver progreso de metas
SELECT name, target_amount, current_amount,
       (current_amount / target_amount * 100) as progress_percent
FROM goals_financialgoal;
```

## 🧪 Testing

### **Ejecutar Pruebas**

```bash
# Todas las pruebas
python manage.py test

# Prueba de un módulo específico
python manage.py test api.accounts

# Pruebas con coverage
coverage run --source='.' manage.py test
coverage report
```

### **Probar Endpoints**

```bash
# Script de prueba incluido
python test_all_endpoints.py

# Con usuario demo
python test_all_endpoints.py --user demo --password demo123
```

### **Datos de Prueba**

El comando `setup_all` crea automáticamente:

- ✅ **Usuario demo** con perfil completo
- ✅ **4 cuentas bancarias** (Corriente, Ahorros, Inversión, Crédito)
- ✅ **50+ transacciones** realistas de los últimos 6 meses
- ✅ **20+ categorías** predefinidas
- ✅ **5 metas financieras** con progreso
- ✅ **Métricas y reportes** precalculados

## 📚 Documentación Adicional

### **🔗 Enlaces Útiles**

- **Django REST Framework**: https://www.django-rest-framework.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **JWT Authentication**: https://django-rest-framework-simplejwt.readthedocs.io/

### **📁 Archivos de Configuración**

- `backend/settings.py` - Configuración principal de Django
- `requirements.txt` - Dependencias del proyecto
- `.env` - Variables de entorno (crear desde .env.example)
- `render.yaml` - Configuración para despliegue

### **🚀 Próximos Pasos**

1. **Ejecutar servidor**: `python manage.py runserver`
2. **Probar API**: Usar Postman o el script de pruebas
3. **Configurar frontend**: React app en `../frontend/`
4. **Personalizar**: Agregar funcionalidades específicas

---

## 🤝 Contribución

### **Estructura para Nuevos Módulos**

```
api/nuevo_modulo/
├── __init__.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── admin.py
├── filters.py
├── management/
│   └── commands/
└── migrations/
    └── __init__.py
```

### **Agregar Nuevo Módulo**

1. Crear estructura de archivos
2. Agregar a `INSTALLED_APPS` en settings.py
3. Crear migraciones: `python manage.py makemigrations nuevo_modulo`
4. Aplicar migraciones: `python manage.py migrate`
5. Agregar URLs al routing principal

---

**🎉 ¡FinTrack Backend está listo para usar!**

Para soporte o preguntas, revisa la documentación de cada módulo o consulta los comandos de ayuda:

```bash
python manage.py help
python manage.py help setup_all
```
