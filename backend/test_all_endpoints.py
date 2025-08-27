#!/usr/bin/env python3
"""
🧪 TEST_ALL_ENDPOINTS.PY - FinTrack Sistema Completo de Testing
===============================================================

Pruebas automáticas para todos los endpoints del sistema FinTrack
- CORE: Autenticación y setup
- ACCOUNTS: Cuentas y filtros  
- TRANSACTIONS: Transacciones, categorías y alertas
- ANALYTICS: Reportes y análisis
- GOALS: Metas financieras y contribuciones

Uso: python test_all_endpoints.py
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
import time

# =============================================================================
# 🔧 CONFIGURACIÓN
# =============================================================================

# URL base del API (cambiar según entorno)
BASE_URL = "http://localhost:8000/api"
# BASE_URL = "https://your-deployed-api.com/api"

# Configuración de testing
TEST_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'demo_user_credentials': None,
    'tokens': None,
    'created_resources': {
        'accounts': [],
        'transactions': [],
        'goals': [],
        'categories': []
    }
}

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'  
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =============================================================================
# 🛠️ UTILIDADES
# =============================================================================

def print_section(title):
    """Imprime sección con formato"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}🧪 {title}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}")

def print_test(endpoint, method="GET", description=""):
    """Imprime test en progreso"""
    print(f"{Colors.YELLOW}🔄 [{method}] {endpoint}{Colors.END}")
    if description:
        print(f"   {description}")

def print_success(message):
    """Imprime éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """Imprime error"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")

def print_info(message):
    """Imprime información"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")

def make_request(method, endpoint, data=None, params=None, headers=None, auth_required=True):
    """Realiza request con manejo de errores y retry"""
    url = f"{BASE_URL}{endpoint}"
    
    # Headers por defecto
    default_headers = {'Content-Type': 'application/json'}
    
    # Agregar autenticación si es requerida
    if auth_required and TEST_CONFIG.get('tokens', {}).get('access'):
        default_headers['Authorization'] = f"Bearer {TEST_CONFIG['tokens']['access']}"
    
    if headers:
        default_headers.update(headers)
    
    # Realizar request con reintentos
    for attempt in range(TEST_CONFIG['max_retries']):
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=default_headers,
                timeout=TEST_CONFIG['timeout']
            )
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == TEST_CONFIG['max_retries'] - 1:
                print_error(f"Error de conexión después de {TEST_CONFIG['max_retries']} intentos: {str(e)}")
                return None
            time.sleep(1)  # Esperar antes del retry
    
    return None

def validate_response(response, expected_status=200, endpoint=""):
    """Valida respuesta del servidor"""
    if response is None:
        print_error(f"No se pudo conectar al endpoint: {endpoint}")
        return False
    
    if response.status_code != expected_status:
        print_error(f"Status {response.status_code} (esperado {expected_status})")
        try:
            error_data = response.json()
            print_error(f"Error: {error_data}")
        except:
            print_error(f"Respuesta: {response.text[:200]}")
        return False
    
    try:
        data = response.json()
        print_success(f"Status {response.status_code} - Respuesta válida")
        return data
    except json.JSONDecodeError:
        print_error("Respuesta no es JSON válido")
        return False

# =============================================================================
# 🔐 MÓDULO CORE - AUTENTICACIÓN Y SETUP
# =============================================================================

def test_core_module():
    """Prueba todos los endpoints del módulo CORE"""
    print_section("MÓDULO CORE - AUTENTICACIÓN Y SETUP")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 1. Test Setup - Migraciones
    print_test("/setup/run-migrations/", "POST", "Ejecutar migraciones")
    results['total'] += 1
    
    response = make_request("POST", "/setup/run-migrations/", auth_required=False)
    data = validate_response(response, 200, "/setup/run-migrations/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Migraciones ejecutadas correctamente")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error ejecutando migraciones")
    
    # 2. Test Setup - Crear Superusuario
    print_test("/setup/create-superuser/", "POST", "Crear superusuario")
    results['total'] += 1
    
    response = make_request("POST", "/setup/create-superuser/", auth_required=False)

    if response.status_code == 201:
        data = response.json()
        if data.get('status') == 'success':
            results['passed'] += 1
            results['details'].append("✅ Superusuario creado correctamente")
    elif response.status_code == 400:
        data = response.json()
        if 'already exists' in data.get('message', ''):
            results['passed'] += 1
            results['details'].append("✅ Superusuario ya existe")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error creando superusuario")
    else:
        results['failed'] += 1
        results['details'].append(f"❌ Status inesperado: {response.status_code}")
    
    # 3. Test Crear Usuario Demo
    print_test("/auth/demo/", "POST", "Crear usuario demo con datos")
    results['total'] += 1
    
    response = make_request("POST", "/auth/demo/", auth_required=False)
    data = validate_response(response, 200, "/auth/demo/")
    
    if data and data.get('access') and data.get('refresh'):
        # Guardar tokens para siguientes pruebas
        TEST_CONFIG['tokens'] = {
            'access': data['access'],
            'refresh': data['refresh']
        }
        results['passed'] += 1
        results['details'].append("✅ Usuario demo creado con tokens JWT")
        print_info(f"Token obtenido: {data['access'][:50]}...")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error creando usuario demo")
        print_error("No se pudieron obtener tokens - las pruebas autenticadas fallarán")
    
    # 4. Test JWT Token Refresh
    if TEST_CONFIG.get('tokens', {}).get('refresh'):
        print_test("/token/refresh/", "POST", "Refrescar token JWT")
        results['total'] += 1
        
        refresh_data = {"refresh": TEST_CONFIG['tokens']['refresh']}
        response = make_request("POST", "/token/refresh/", data=refresh_data, auth_required=False)
        data = validate_response(response, 200, "/token/refresh/")
        
        if data and data.get('access'):
            # Actualizar token
            TEST_CONFIG['tokens']['access'] = data['access']
            results['passed'] += 1
            results['details'].append("✅ Token JWT refrescado exitosamente")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error refrescando token JWT")
    
    # 5. Test Perfil de Usuario
    if TEST_CONFIG.get('tokens', {}).get('access'):
        print_test("/auth/profile/", "GET", "Obtener perfil del usuario autenticado")
        results['total'] += 1
        
        response = make_request("GET", "/auth/profile/")
        data = validate_response(response, 200, "/auth/profile/")
        
        if data and 'username' in data:
            results['passed'] += 1
            results['details'].append(f"✅ Perfil obtenido - Usuario: {data.get('username')}")
            print_info(f"Usuario demo: {data.get('username')}, Es demo: {data.get('is_demo')}")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error obteniendo perfil de usuario")
    
    # 6. Test Registro de Usuario Normal (opcional)
    print_test("/auth/register/", "POST", "Registro de usuario normal")
    results['total'] += 1
    
    register_data = {
        "username": f"test_user_{int(time.time())}",
        "email": f"test_{int(time.time())}@fintrack.com",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    response = make_request("POST", "/auth/register/", data=register_data, auth_required=False)
    data = validate_response(response, 201, "/auth/register/")
    
    if data and data.get('user_id'):
        results['passed'] += 1
        results['details'].append("✅ Usuario normal registrado exitosamente")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error registrando usuario normal")
    
    return results

# =============================================================================
# 🏦 MÓDULO ACCOUNTS - CUENTAS Y FILTROS
# =============================================================================

def test_accounts_module():
    """Prueba todos los endpoints del módulo ACCOUNTS"""
    print_section("MÓDULO ACCOUNTS - CUENTAS Y FILTROS")
    
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_error("No hay token de autenticación - saltando pruebas de ACCOUNTS")
        return {'total': 0, 'passed': 0, 'failed': 0, 'details': ['❌ Sin autenticación']}
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 1. Test Listar Cuentas - CORREGIDO
    print_test("/accounts/", "GET", "Listar todas las cuentas del usuario")
    results['total'] += 1
    
    response = make_request("GET", "/accounts/")
    data = validate_response(response, 200, "/accounts/")
    
    if data:
        # FIX: Manejar tanto formato paginado como lista directa
        if isinstance(data, dict) and 'results' in data:
            # Formato paginado: {'results': [...], 'count': X}
            accounts_list = data['results']
            accounts_count = len(accounts_list)
        elif isinstance(data, list):
            # Formato lista directa: [...]
            accounts_list = data
            accounts_count = len(accounts_list)
        else:
            accounts_list = []
            accounts_count = 0
        
        results['passed'] += 1
        results['details'].append(f"✅ Cuentas listadas: {accounts_count} encontradas")
        print_info(f"Cuentas demo disponibles: {accounts_count}")
        
        # Guardar IDs de cuentas para otros tests
        TEST_CONFIG['created_resources']['accounts'] = [acc['id'] for acc in accounts_list if 'id' in acc]
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando cuentas")
    
    # 2. Test Crear Nueva Cuenta
    print_test("/accounts/", "POST", "Crear nueva cuenta de ahorro")
    results['total'] += 1
    
    new_account_data = {
        "name": "Cuenta Test",
        "bank_name": "Banco Test",
        "account_type": "savings",
        "initial_balance": "1000.00",
        "currency": "PEN"
    }
    
    response = make_request("POST", "/accounts/", data=new_account_data)
    data = validate_response(response, 201, "/accounts/")
    
    if data and data.get('id'):
        new_account_id = data['id']
        if 'accounts' not in TEST_CONFIG['created_resources']:
            TEST_CONFIG['created_resources']['accounts'] = []
        TEST_CONFIG['created_resources']['accounts'].append(new_account_id)
        results['passed'] += 1
        results['details'].append(f"✅ Cuenta creada - ID: {new_account_id}")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error creando cuenta")
    
    # 3. Test Obtener Cuenta Específica
    if TEST_CONFIG['created_resources'].get('accounts'):
        account_id = TEST_CONFIG['created_resources']['accounts'][0]
        print_test(f"/accounts/{account_id}/", "GET", "Obtener detalles de cuenta específica")
        results['total'] += 1
        
        response = make_request("GET", f"/accounts/{account_id}/")
        data = validate_response(response, 200, f"/accounts/{account_id}/")
        
        if data and data.get('id') == account_id:
            results['passed'] += 1
            results['details'].append(f"✅ Cuenta específica obtenida - {data.get('name', 'N/A')}")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error obteniendo cuenta específica")
    
    # 4. Test Resumen Financiero Global
    print_test("/accounts/summary/", "GET", "Resumen financiero global")
    results['total'] += 1
    
    response = make_request("GET", "/accounts/summary/")
    data = validate_response(response, 200, "/accounts/summary/")
    
    if data and 'total_balance' in data:
        results['passed'] += 1
        results['details'].append(f"✅ Resumen obtenido - Balance total: ${data.get('total_balance', 0)}")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo resumen financiero")
    
    # 5. Test Filtros - Cuentas Activas
    print_test("/accounts/?is_active=true", "GET", "Filtrar solo cuentas activas")
    results['total'] += 1
    
    response = make_request("GET", "/accounts/", params={"is_active": "true"})
    data = validate_response(response, 200, "/accounts/ con filtro is_active")
    
    if data is not None:
        results['passed'] += 1
        results['details'].append("✅ Filtro is_active funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro is_active")
    
    # 6. Test Filtros - Por Tipo de Cuenta
    print_test("/accounts/?account_type=checking", "GET", "Filtrar cuentas corrientes")
    results['total'] += 1
    
    response = make_request("GET", "/accounts/", params={"account_type": "checking"})
    data = validate_response(response, 200, "/accounts/ con filtro account_type")
    
    if data is not None:
        results['passed'] += 1
        results['details'].append("✅ Filtro account_type funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro account_type")
    
    # 7. Test Filtros - Rango de Balance
    print_test("/accounts/?min_balance=1000&max_balance=10000", "GET", "Filtrar por rango de balance")
    results['total'] += 1
    
    response = make_request("GET", "/accounts/", params={"min_balance": "1000", "max_balance": "10000"})
    data = validate_response(response, 200, "/accounts/ con filtros de balance")
    
    if data is not None:
        results['passed'] += 1
        results['details'].append("✅ Filtros de balance funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtros de balance")
    
    # 8. Test Historial de Balance
    if TEST_CONFIG['created_resources'].get('accounts'):
        account_id = TEST_CONFIG['created_resources']['accounts'][0]
        print_test(f"/accounts/{account_id}/balance_history/", "GET", "Historial de balance (30 días)")
        results['total'] += 1
        
        response = make_request("GET", f"/accounts/{account_id}/balance_history/")
        data = validate_response(response, 200, f"/accounts/{account_id}/balance_history/")
        
        if data is not None:
            results['passed'] += 1
            results['details'].append("✅ Historial de balance obtenido")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error obteniendo historial de balance")
    
    # 9. Test Transacciones de Cuenta
    if TEST_CONFIG['created_resources'].get('accounts'):
        account_id = TEST_CONFIG['created_resources']['accounts'][0]
        print_test(f"/accounts/{account_id}/transactions/", "GET", "Transacciones de cuenta específica")
        results['total'] += 1
        
        response = make_request("GET", f"/accounts/{account_id}/transactions/")
        data = validate_response(response, 200, f"/accounts/{account_id}/transactions/")
        
        if data is not None:
            # FIX: Manejar respuesta como lista o dict paginado
            if isinstance(data, dict) and 'results' in data:
                transactions_count = len(data['results'])
            elif isinstance(data, list):
                transactions_count = len(data)
            else:
                transactions_count = 0
                
            results['passed'] += 1
            results['details'].append(f"✅ Transacciones de cuenta: {transactions_count} encontradas")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error obteniendo transacciones de cuenta")
    
    # 10. Test Conciliación de Cuenta (NUEVO)
    if TEST_CONFIG['created_resources'].get('accounts'):
        account_id = TEST_CONFIG['created_resources']['accounts'][-1]  # Usar cuenta creada en test
        print_test(f"/accounts/{account_id}/reconcile/", "POST", "Conciliar balance de cuenta")
        results['total'] += 1
        
        reconcile_data = {"real_balance": "1050.00"}
        response = make_request("POST", f"/accounts/{account_id}/reconcile/", data=reconcile_data)
        data = validate_response(response, 200, f"/accounts/{account_id}/reconcile/")
        
        if data and 'message' in data:
            results['passed'] += 1
            results['details'].append(f"✅ Conciliación completada - Diferencia: ${data.get('difference', 0)}")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error en conciliación")
    
    return results

# =============================================================================
# 💳 MÓDULO TRANSACTIONS - TRANSACCIONES, CATEGORÍAS Y ALERTAS
# =============================================================================

def test_transactions_module():
    """Prueba todos los endpoints del módulo TRANSACTIONS"""
    print_section("MÓDULO TRANSACTIONS - TRANSACCIONES, CATEGORÍAS Y ALERTAS")
    
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_error("No hay token de autenticación - saltando pruebas de TRANSACTIONS")
        return {'total': 0, 'passed': 0, 'failed': 0, 'details': ['❌ Sin autenticación']}
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # === CATEGORÍAS FIRST (necesarias para transacciones) ===
    
    # 1. Test Crear Categorías por Defecto
    print_test("/categories/create_defaults/", "POST", "Crear categorías predeterminadas")
    results['total'] += 1
    
    response = make_request("POST", "/categories/create_defaults/")
    data = validate_response(response, 201, "/categories/create_defaults/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Categorías por defecto creadas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error creando categorías por defecto")
    
    # 2. Test Listar Categorías
    print_test("/categories/", "GET", "Listar todas las categorías")
    results['total'] += 1
    
    response = make_request("GET", "/categories/")
    data = validate_response(response, 200, "/categories/")
    
    if data:
        categories_count = len(data.get('results', data))
        results['passed'] += 1
        results['details'].append(f"✅ Categorías listadas: {categories_count} encontradas")
        
        # Guardar IDs de categorías
        if isinstance(data, dict) and 'results' in data:
            TEST_CONFIG['created_resources']['categories'] = [cat['id'] for cat in data['results'][:3]]
        elif isinstance(data, list):
            TEST_CONFIG['created_resources']['categories'] = [cat['id'] for cat in data[:3]]
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando categorías")
    
    # 3. Test Categorías por Tipo
    print_test("/categories/by_type/", "GET", "Categorías agrupadas por tipo")
    results['total'] += 1
    
    response = make_request("GET", "/categories/by_type/")
    data = validate_response(response, 200, "/categories/by_type/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Categorías agrupadas por tipo obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo categorías por tipo")
    
    # === TRANSACCIONES ===
    
    # 4. Test Listar Transacciones
    print_test("/transactions/", "GET", "Listar todas las transacciones")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/")
    data = validate_response(response, 200, "/transactions/")
    
    if data:
        transactions_count = len(data.get('results', data))
        results['passed'] += 1
        results['details'].append(f"✅ Transacciones listadas: {transactions_count} encontradas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando transacciones")
    
    # 5. Test Crear Nueva Transacción
    if TEST_CONFIG['created_resources']['accounts'] and TEST_CONFIG['created_resources']['categories']:
        print_test("/transactions/", "POST", "Crear nueva transacción de gasto")
        results['total'] += 1
        
        new_transaction_data = {
            "title": "Compra Test",
            "description": "Transacción de prueba automatizada",
            "amount": "50.00",
            "type": "expense",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "from_account": TEST_CONFIG['created_resources']['accounts'][0],
            "category": TEST_CONFIG['created_resources']['categories'][0]
        }
        
        response = make_request("POST", "/transactions/", data=new_transaction_data)
        data = validate_response(response, 201, "/transactions/")
        
        if data and data.get('id'):
            new_transaction_id = data['id']
            TEST_CONFIG['created_resources']['transactions'].append(new_transaction_id)
            results['passed'] += 1
            results['details'].append(f"✅ Transacción creada - ID: {new_transaction_id}")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error creando transacción")
    
    # 6. Test Transacciones Recientes
    print_test("/transactions/recent/", "GET", "Últimas 10 transacciones")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/recent/")
    data = validate_response(response, 200, "/transactions/recent/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Transacciones recientes obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo transacciones recientes")
    
    # 7. Test Dashboard de Transacciones
    print_test("/transactions/dashboard/", "GET", "Dashboard con métricas del período")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/dashboard/")
    data = validate_response(response, 200, "/transactions/dashboard/")
    
    if data and 'metrics' in data:
        results['passed'] += 1
        results['details'].append("✅ Dashboard de transacciones obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo dashboard de transacciones")
    
    # 8. Test Transacciones por Tipo
    print_test("/transactions/by_type/", "GET", "Transacciones agrupadas por tipo")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/by_type/")
    data = validate_response(response, 200, "/transactions/by_type/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Transacciones agrupadas por tipo obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo transacciones por tipo")
    
    # 9. Test Búsqueda de Transacciones
    print_test("/transactions/search/?q=test", "GET", "Búsqueda avanzada de transacciones")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/search/", params={"q": "test"})
    data = validate_response(response, 200, "/transactions/search/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Búsqueda de transacciones funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error en búsqueda de transacciones")
    
    # 10. Test Filtros de Transacciones - Por Tipo
    print_test("/transactions/?type=expense", "GET", "Filtrar solo gastos")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/", params={"type": "expense"})
    data = validate_response(response, 200, "/transactions/ con filtro type")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtro por tipo funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro por tipo")
    
    # 11. Test Filtros - Rango de Fechas
    print_test("/transactions/?date_after=2024-01-01", "GET", "Filtrar por fecha")
    results['total'] += 1
    
    response = make_request("GET", "/transactions/", params={
        "date_after": "2024-01-01",
        "date_before": "2024-12-31"
    })
    data = validate_response(response, 200, "/transactions/ con filtros de fecha")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtros de fecha funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtros de fecha")
    
    # 12. Test Alertas de Presupuesto
    print_test("/budget-alerts/", "GET", "Listar alertas de presupuesto")
    results['total'] += 1
    
    response = make_request("GET", "/budget-alerts/")  
    data = validate_response(response, 200, "/budget-alerts/")
    
    if data:
        alerts_count = len(data.get('results', data))
        results['passed'] += 1
        results['details'].append(f"✅ Alertas listadas: {alerts_count} encontradas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando alertas de presupuesto")
    
    # 13. Test Alertas No Leídas
    print_test("/budget-alerts/unread/", "GET", "Alertas no leídas")
    results['total'] += 1
    
    response = make_request("GET", "/budget-alerts/unread/")
    data = validate_response(response, 200, "/budget-alerts/unread/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Alertas no leídas obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo alertas no leídas")
    
    return results

# =============================================================================
# 📊 MÓDULO ANALYTICS - REPORTES Y ANÁLISIS
# =============================================================================

def test_analytics_module():
    """Prueba todos los endpoints del módulo ANALYTICS"""
    print_section("MÓDULO ANALYTICS - REPORTES Y ANÁLISIS")
    
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_error("No hay token de autenticación - saltando pruebas de ANALYTICS")
        return {'total': 0, 'passed': 0, 'failed': 0, 'details': ['❌ Sin autenticación']}
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 1. Test Métricas Principales
    print_test("/reports/metrics/", "GET", "Métricas principales con comparativas")
    results['total'] += 1
    
    response = make_request("GET", "/reports/metrics/")
    data = validate_response(response, 200, "/reports/metrics/")
    
    if data and 'metrics' in data:
        results['passed'] += 1
        results['details'].append("✅ Métricas principales obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo métricas principales")
    
    # 2. Test Ingresos vs Gastos
    print_test("/reports/income-vs-expenses/", "GET", "Gráfico ingresos vs gastos mensual")
    results['total'] += 1
    
    response = make_request("GET", "/reports/income-vs-expenses/")
    data = validate_response(response, 200, "/reports/income-vs-expenses/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Reporte ingresos vs gastos obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo ingresos vs gastos")
    
    # 3. Test Timeline de Balance
    print_test("/reports/balance-timeline/", "GET", "Timeline balance acumulado")
    results['total'] += 1
    
    response = make_request("GET", "/reports/balance-timeline/")
    data = validate_response(response, 200, "/reports/balance-timeline/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Timeline de balance obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo timeline de balance")
    
    # 4. Test Distribución por Categorías
    print_test("/reports/category-distribution/", "GET", "Distribución por categorías (pie)")
    results['total'] += 1
    
    response = make_request("GET", "/reports/category-distribution/")
    data = validate_response(response, 200, "/reports/category-distribution/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Distribución por categorías obtenida")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo distribución por categorías")
    
    # 5. Test Top Categorías
    print_test("/reports/top-categories/", "GET", "Top 5 categorías con tendencias")
    results['total'] += 1
    
    response = make_request("GET", "/reports/top-categories/")
    data = validate_response(response, 200, "/reports/top-categories/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Top categorías obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo top categorías")
    
    # 6. Test Transacciones Recientes (Analytics)
    print_test("/reports/recent-transactions/", "GET", "Transacciones recientes con íconos")
    results['total'] += 1
    
    response = make_request("GET", "/reports/recent-transactions/")
    data = validate_response(response, 200, "/reports/recent-transactions/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Transacciones recientes (analytics) obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo transacciones recientes (analytics)")
    
    # 7. Test Métricas Financieras
    print_test("/reports/financial-metrics/", "GET", "Métricas precalculadas por período")
    results['total'] += 1
    
    response = make_request("GET", "/reports/financial-metrics/")
    data = validate_response(response, 200, "/reports/financial-metrics/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Métricas financieras obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo métricas financieras")
    
    # 8. Test Alertas de Reportes
    print_test("/reports/alerts/", "GET", "Obtener alertas de presupuesto")
    results['total'] += 1
    
    response = make_request("GET", "/reports/alerts/")
    data = validate_response(response, 200, "/reports/alerts/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Alertas de reportes obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo alertas de reportes")
    
    # 9. Test Tendencias de Categorías
    print_test("/reports/category-trends/", "GET", "Tendencias de categorías en tiempo")
    results['total'] += 1
    
    response = make_request("GET", "/reports/category-trends/")
    data = validate_response(response, 200, "/reports/category-trends/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Tendencias de categorías obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo tendencias de categorías")
    
    # 10. Test Dashboard Completo
    print_test("/reports-overview/", "GET", "Dashboard completo (1 llamada)")
    results['total'] += 1
    
    response = make_request("GET", "/reports-overview/")
    data = validate_response(response, 200, "/reports-overview/")
    
    if data and 'metrics' in data and 'charts' in data:
        results['passed'] += 1
        results['details'].append("✅ Dashboard completo obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo dashboard completo")
    
    # 11. Test Ratios Financieros
    print_test("/financial-ratios/", "GET", "Ratios financieros profesionales")
    results['total'] += 1
    
    response = make_request("GET", "/financial-ratios/")
    data = validate_response(response, 200, "/financial-ratios/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Ratios financieros obtenidos")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo ratios financieros")
    
    # 12. Test Filtros - Período Mensual
    print_test("/reports/metrics/?period=monthly", "GET", "Métricas con filtro período mensual")
    results['total'] += 1
    
    response = make_request("GET", "/reports/metrics/", params={"period": "monthly"})
    data = validate_response(response, 200, "/reports/metrics/ con filtro período")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtro de período funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro de período")
    
    # 13. Test Filtros - Fechas Personalizadas
    print_test("/reports/metrics/?start_date=2024-01-01&end_date=2024-12-31", "GET", "Métricas con rango personalizado")
    results['total'] += 1
    
    response = make_request("GET", "/reports/metrics/", params={
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    })
    data = validate_response(response, 200, "/reports/metrics/ con fechas personalizadas")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtros de fechas personalizadas funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtros de fechas personalizadas")
    
    return results

# =============================================================================
# 🎯 MÓDULO GOALS - METAS FINANCIERAS Y CONTRIBUCIONES
# =============================================================================

def test_goals_module():
    """Prueba todos los endpoints del módulo GOALS"""
    print_section("MÓDULO GOALS - METAS FINANCIERAS Y CONTRIBUCIONES")
    
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_error("No hay token de autenticación - saltando pruebas de GOALS")
        return {'total': 0, 'passed': 0, 'failed': 0, 'details': ['❌ Sin autenticación']}
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 1. Test Crear Plantillas de Metas por Defecto
    print_test("/setup/create-goal-templates/", "POST", "Crear plantillas por defecto")
    results['total'] += 1
    
    response = make_request("POST", "/setup/create-goal-templates/")
    data = validate_response(response, 201, "/setup/create-goal-templates/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Plantillas de metas creadas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error creando plantillas de metas")
    
    # 2. Test Listar Plantillas
    print_test("/goal-templates/", "GET", "Listar plantillas disponibles")
    results['total'] += 1
    
    response = make_request("GET", "/goal-templates/")
    data = validate_response(response, 200, "/goal-templates/")
    
    if data:
        templates_count = len(data.get('results', data))
        results['passed'] += 1
        results['details'].append(f"✅ Plantillas listadas: {templates_count} encontradas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando plantillas")
    
    # 3. Test Plantillas por Categoría
    print_test("/goal-templates/by_category/", "GET", "Plantillas agrupadas por tipo")
    results['total'] += 1
    
    response = make_request("GET", "/goal-templates/by_category/")
    data = validate_response(response, 200, "/goal-templates/by_category/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Plantillas agrupadas por categoría obtenidas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo plantillas por categoría")
    
    # 4. Test Crear Meta Financiera
    if TEST_CONFIG['created_resources']['accounts']:
        print_test("/goals/", "POST", "Crear nueva meta financiera")
        results['total'] += 1
        
        new_goal_data = {
            "title": "Meta Test Automatizada",
            "description": "Meta creada por el sistema de testing",
            "goal_type": "savings",
            "target_amount": "5000.00",
            "target_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "priority": "medium",
            "associated_account": TEST_CONFIG['created_resources']['accounts'][0]
        }
        
        response = make_request("POST", "/goals/", data=new_goal_data)
        data = validate_response(response, 201, "/goals/")
        
        if data and data.get('id'):
            new_goal_id = data['id']
            TEST_CONFIG['created_resources']['goals'].append(new_goal_id)
            results['passed'] += 1
            results['details'].append(f"✅ Meta creada - ID: {new_goal_id}")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error creando meta")
    
    # 5. Test Listar Metas
    print_test("/goals/", "GET", "Listar todas las metas")
    results['total'] += 1
    
    response = make_request("GET", "/goals/")
    data = validate_response(response, 200, "/goals/")
    
    if data:
        goals_count = len(data.get('results', data))
        results['passed'] += 1
        results['details'].append(f"✅ Metas listadas: {goals_count} encontradas")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error listando metas")
    
    # 6. Test Dashboard de Metas
    print_test("/goals/dashboard/", "GET", "Dashboard completo de metas")
    results['total'] += 1
    
    response = make_request("GET", "/goals/dashboard/")
    data = validate_response(response, 200, "/goals/dashboard/")
    
    if data and 'summary' in data:
        results['passed'] += 1
        results['details'].append("✅ Dashboard de metas obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo dashboard de metas")
    
    # 7. Test Resumen de Metas
    print_test("/goals/summary/", "GET", "Resumen rápido para widgets")
    results['total'] += 1
    
    response = make_request("GET", "/goals/summary/")
    data = validate_response(response, 200, "/goals/summary/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Resumen de metas obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo resumen de metas")
    
    # 8. Test Agregar Contribución a Meta
    if TEST_CONFIG['created_resources']['goals'] and TEST_CONFIG['created_resources']['accounts']:
        goal_id = TEST_CONFIG['created_resources']['goals'][0]
        print_test(f"/goals/{goal_id}/add_contribution/", "POST", "Agregar contribución a meta")
        results['total'] += 1
        
        contribution_data = {
            "amount": "100.00",
            "from_account": TEST_CONFIG['created_resources']['accounts'][0],
            "notes": "Contribución de prueba automatizada",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = make_request("POST", f"/goals/{goal_id}/add_contribution/", data=contribution_data)
        data = validate_response(response, 201, f"/goals/{goal_id}/add_contribution/")
        
        if data:
            results['passed'] += 1
            results['details'].append("✅ Contribución agregada exitosamente")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error agregando contribución")
    
    # 9. Test Ver Contribuciones de Meta
    if TEST_CONFIG['created_resources']['goals']:
        goal_id = TEST_CONFIG['created_resources']['goals'][0]
        print_test(f"/goals/{goal_id}/contributions/", "GET", "Ver contribuciones de meta")
        results['total'] += 1
        
        response = make_request("GET", f"/goals/{goal_id}/contributions/")
        data = validate_response(response, 200, f"/goals/{goal_id}/contributions/")
        
        if data:
            contributions_count = len(data.get('results', data))
            results['passed'] += 1
            results['details'].append(f"✅ Contribuciones listadas: {contributions_count} encontradas")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error listando contribuciones")
    
    # 10. Test Análisis de Meta
    if TEST_CONFIG['created_resources']['goals']:
        goal_id = TEST_CONFIG['created_resources']['goals'][0]
        print_test(f"/goals/{goal_id}/analytics/", "GET", "Análisis detallado de meta")
        results['total'] += 1
        
        response = make_request("GET", f"/goals/{goal_id}/analytics/")
        data = validate_response(response, 200, f"/goals/{goal_id}/analytics/")
        
        if data:
            results['passed'] += 1
            results['details'].append("✅ Análisis de meta obtenido")
        else:
            results['failed'] += 1
            results['details'].append("❌ Error obteniendo análisis de meta")
    
    # 11. Test Calendario de Metas
    print_test("/goals-calendar/", "GET", "Vista calendario de metas")
    results['total'] += 1
    
    current_date = datetime.now()
    response = make_request("GET", "/goals-calendar/", params={
        "year": current_date.year,
        "month": current_date.month
    })
    data = validate_response(response, 200, "/goals-calendar/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Calendario de metas obtenido")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo calendario de metas")
    
    # 12. Test Insights Inteligentes
    print_test("/goals-insights/", "GET", "Insights inteligentes")
    results['total'] += 1
    
    response = make_request("GET", "/goals-insights/")
    data = validate_response(response, 200, "/goals-insights/")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Insights inteligentes obtenidos")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error obteniendo insights inteligentes")
    
    # 13. Test Filtros - Metas Activas
    print_test("/goals/?status=active", "GET", "Filtrar solo metas activas")
    results['total'] += 1
    
    response = make_request("GET", "/goals/", params={"status": "active"})
    data = validate_response(response, 200, "/goals/ con filtro status")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtro por status funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro por status")
    
    # 14. Test Filtros - Por Tipo de Meta
    print_test("/goals/?goal_type=savings", "GET", "Filtrar metas de ahorro")
    results['total'] += 1
    
    response = make_request("GET", "/goals/", params={"goal_type": "savings"})
    data = validate_response(response, 200, "/goals/ con filtro goal_type")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtro por tipo de meta funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtro por tipo de meta")
    
    # 15. Test Filtros - Rango de Progreso
    print_test("/goals/?min_progress=25&max_progress=75", "GET", "Filtrar por rango de progreso")
    results['total'] += 1
    
    response = make_request("GET", "/goals/", params={"min_progress": "25", "max_progress": "75"})
    data = validate_response(response, 200, "/goals/ con filtros de progreso")
    
    if data:
        results['passed'] += 1
        results['details'].append("✅ Filtros de progreso funcionando")
    else:
        results['failed'] += 1
        results['details'].append("❌ Error con filtros de progreso")
    
    return results

# =============================================================================
# 📊 FUNCIÓN PRINCIPAL DE TESTING
# =============================================================================

def run_all_tests():
    """Ejecuta todas las pruebas y genera reporte final"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🧪 INICIANDO TESTING COMPLETO DE FINTRACK")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.END}")
    
    # Resultados consolidados
    total_results = {
        'modules': {},
        'total_tests': 0,
        'total_passed': 0,
        'total_failed': 0,
        'start_time': datetime.now(),
        'end_time': None
    }
    
    # === EJECUTAR TESTS POR MÓDULO ===
    
    # 1. CORE
    try:
        core_results = test_core_module()
        total_results['modules']['CORE'] = core_results
        total_results['total_tests'] += core_results['total']
        total_results['total_passed'] += core_results['passed']
        total_results['total_failed'] += core_results['failed']
    except Exception as e:
        print_error(f"Error crítico en módulo CORE: {str(e)}")
        total_results['modules']['CORE'] = {'total': 0, 'passed': 0, 'failed': 1, 'details': [f"❌ Error crítico: {str(e)}"]}
        total_results['total_failed'] += 1
    
    # 2. ACCOUNTS
    try:
        accounts_results = test_accounts_module()
        total_results['modules']['ACCOUNTS'] = accounts_results
        total_results['total_tests'] += accounts_results['total']
        total_results['total_passed'] += accounts_results['passed']
        total_results['total_failed'] += accounts_results['failed']
    except Exception as e:
        print_error(f"Error crítico en módulo ACCOUNTS: {str(e)}")
        total_results['modules']['ACCOUNTS'] = {'total': 0, 'passed': 0, 'failed': 1, 'details': [f"❌ Error crítico: {str(e)}"]}
        total_results['total_failed'] += 1
    
    # 3. TRANSACTIONS
    try:
        transactions_results = test_transactions_module()
        total_results['modules']['TRANSACTIONS'] = transactions_results
        total_results['total_tests'] += transactions_results['total']
        total_results['total_passed'] += transactions_results['passed']
        total_results['total_failed'] += transactions_results['failed']
    except Exception as e:
        print_error(f"Error crítico en módulo TRANSACTIONS: {str(e)}")
        total_results['modules']['TRANSACTIONS'] = {'total': 0, 'passed': 0, 'failed': 1, 'details': [f"❌ Error crítico: {str(e)}"]}
        total_results['total_failed'] += 1
    
    # 4. ANALYTICS
    try:
        analytics_results = test_analytics_module()
        total_results['modules']['ANALYTICS'] = analytics_results
        total_results['total_tests'] += analytics_results['total']
        total_results['total_passed'] += analytics_results['passed']
        total_results['total_failed'] += analytics_results['failed']
    except Exception as e:
        print_error(f"Error crítico en módulo ANALYTICS: {str(e)}")
        total_results['modules']['ANALYTICS'] = {'total': 0, 'passed': 0, 'failed': 1, 'details': [f"❌ Error crítico: {str(e)}"]}
        total_results['total_failed'] += 1
    
    # 5. GOALS
    try:
        goals_results = test_goals_module()
        total_results['modules']['GOALS'] = goals_results
        total_results['total_tests'] += goals_results['total']
        total_results['total_passed'] += goals_results['passed']
        total_results['total_failed'] += goals_results['failed']
    except Exception as e:
        print_error(f"Error crítico en módulo GOALS: {str(e)}")
        total_results['modules']['GOALS'] = {'total': 0, 'passed': 0, 'failed': 1, 'details': [f"❌ Error crítico: {str(e)}"]}
        total_results['total_failed'] += 1
    
    total_results['end_time'] = datetime.now()
    
    # === GENERAR REPORTE FINAL ===
    generate_final_report(total_results)
    
    return total_results

def generate_final_report(results):
    """Genera reporte final completo"""
    print_section("REPORTE FINAL DE TESTING")
    
    # Calcular duración
    duration = results['end_time'] - results['start_time']
    
    # Resumen general
    print(f"{Colors.BOLD}📊 RESUMEN GENERAL:{Colors.END}")
    print(f"  Total de tests ejecutados: {Colors.BOLD}{results['total_tests']}{Colors.END}")
    print(f"  Tests exitosos: {Colors.GREEN}{results['total_passed']}{Colors.END}")
    print(f"  Tests fallidos: {Colors.RED}{results['total_failed']}{Colors.END}")
    print(f"  Duración total: {Colors.CYAN}{duration.total_seconds():.2f} segundos{Colors.END}")
    
    # Calcular porcentaje de éxito
    if results['total_tests'] > 0:
        success_rate = (results['total_passed'] / results['total_tests']) * 100
        print(f"  Tasa de éxito: {Colors.BOLD}{success_rate:.1f}%{Colors.END}")
    
    print()
    
    # Resultados por módulo
    print(f"{Colors.BOLD}📋 RESULTADOS POR MÓDULO:{Colors.END}")
    
    for module_name, module_results in results['modules'].items():
        total = module_results['total']
        passed = module_results['passed']
        failed = module_results['failed']
        
        if total > 0:
            success_rate = (passed / total) * 100
            status_color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED
        else:
            success_rate = 0
            status_color = Colors.RED
        
        print(f"\n  {Colors.BOLD}{module_name}:{Colors.END}")
        print(f"    Tests: {total} | Exitosos: {status_color}{passed}{Colors.END} | Fallidos: {Colors.RED}{failed}{Colors.END} | Éxito: {status_color}{success_rate:.1f}%{Colors.END}")
        
        # Mostrar detalles
        for detail in module_results['details']:
            print(f"    {detail}")
    
    # Status final
    print(f"\n{Colors.BOLD}🏁 STATUS FINAL:{Colors.END}")
    
    if results['total_failed'] == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 TODOS LOS TESTS PASARON EXITOSAMENTE!{Colors.END}")
        print(f"{Colors.GREEN}El sistema FinTrack está funcionando correctamente.{Colors.END}")
    elif results['total_passed'] > results['total_failed']:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ ALGUNOS TESTS FALLARON{Colors.END}")
        print(f"{Colors.YELLOW}El sistema funciona parcialmente. Revisar errores.{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}🚨 MÚLTIPLES FALLAS DETECTADAS{Colors.END}")
        print(f"{Colors.RED}El sistema requiere atención inmediata.{Colors.END}")
    
    # Información adicional
    print(f"\n{Colors.BLUE}💡 INFORMACIÓN ADICIONAL:{Colors.END}")
    
    if TEST_CONFIG.get('tokens'):
        print(f"  ✅ Token JWT obtenido y válido")
    else:
        print(f"  ❌ No se pudo obtener token JWT")
    
    accounts_count = len(TEST_CONFIG['created_resources']['accounts'])
    transactions_count = len(TEST_CONFIG['created_resources']['transactions'])
    goals_count = len(TEST_CONFIG['created_resources']['goals'])
    
    print(f"  📊 Recursos creados durante testing:")
    print(f"    - Cuentas: {accounts_count}")
    print(f"    - Transacciones: {transactions_count}")
    print(f"    - Metas: {goals_count}")
    
    # Recomendaciones
    print(f"\n{Colors.CYAN}🎯 RECOMENDACIONES:{Colors.END}")
    
    if results['total_failed'] > 0:
        print(f"  • Revisar logs del servidor para errores específicos")
        print(f"  • Verificar configuración de base de datos")
        print(f"  • Comprobar variables de entorno")
        print(f"  • Validar permisos de autenticación")
    
    print(f"  • Ejecutar migraciones si es necesario: python manage.py migrate")
    print(f"  • Verificar que el servidor esté ejecutándose en: {BASE_URL}")
    
    print(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}🧪 TESTING COMPLETADO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.CYAN}{'='*80}{Colors.END}")

# =============================================================================
# 🚀 PUNTO DE ENTRADA
# =============================================================================

def generate_module_report(module_name, results):
    """Genera reporte para un módulo específico"""
    print_section(f"REPORTE DE MÓDULO {module_name}")
    
    total = results['total']
    passed = results['passed']
    failed = results['failed']
    
    print(f"{Colors.BOLD}📊 RESUMEN DE {module_name}:{Colors.END}")
    print(f"  Total de tests: {total}")
    print(f"  Tests exitosos: {Colors.GREEN}{passed}{Colors.END}")
    print(f"  Tests fallidos: {Colors.RED}{failed}{Colors.END}")
    
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"  Tasa de éxito: {Colors.BOLD}{success_rate:.1f}%{Colors.END}")
    
    print(f"\n{Colors.BOLD}📋 DETALLES:{Colors.END}")
    for detail in results['details']:
        print(f"  {detail}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}✅ Módulo {module_name} funcionando correctamente!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Módulo {module_name} requiere atención.{Colors.END}")

def cleanup_test_resources():
    """Limpia recursos creados durante el testing"""
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_warning("No hay token de autenticación - saltando cleanup")
        return
    
    print_info("🧹 Iniciando limpieza de recursos de prueba...")
    cleanup_count = 0
    
    # Limpiar transacciones creadas
    for transaction_id in TEST_CONFIG['created_resources']['transactions']:
        try:
            response = make_request("DELETE", f"/transactions/{transaction_id}/")
            if response and response.status_code == 204:
                cleanup_count += 1
        except:
            pass  # Ignorar errores de cleanup
    
    # Limpiar metas creadas
    for goal_id in TEST_CONFIG['created_resources']['goals']:
        try:
            response = make_request("DELETE", f"/goals/{goal_id}/")
            if response and response.status_code == 204:
                cleanup_count += 1
        except:
            pass  # Ignorar errores de cleanup
    
    # Limpiar cuentas creadas (solo las que creamos nosotros)
    for account_id in TEST_CONFIG['created_resources']['accounts']:
        # Solo intentar eliminar si sabemos que la creamos nosotros
        # (las cuentas demo no se deben eliminar)
        try:
            account_response = make_request("GET", f"/accounts/{account_id}/")
            if account_response and account_response.status_code == 200:
                account_data = account_response.json()
                if account_data.get('name') == 'Cuenta Test':  # Solo nuestras cuentas de prueba
                    delete_response = make_request("DELETE", f"/accounts/{account_id}/")
                    if delete_response and delete_response.status_code == 204:
                        cleanup_count += 1
        except:
            pass  # Ignorar errores de cleanup
    
    if cleanup_count > 0:
        print_success(f"✅ Limpieza completada - {cleanup_count} recursos eliminados")
    else:
        print_info("ℹ️ No hay recursos para limpiar")

if __name__ == "__main__":
    print(f"{Colors.BOLD}🚀 FinTrack Test Suite v1.0{Colors.END}")
    print(f"Desarrollado para pruebas automáticas del sistema FinTrack")
    print()
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Uso: python test_all_endpoints.py [opciones]")
            print("Opciones:")
            print("  --help, -h       Mostrar esta ayuda")
            print("  --url URL        Especificar URL base personalizada")
            print("  --timeout N      Timeout en segundos (default: 30)")
            print("  --no-cleanup     No limpiar recursos creados")
            print("  --module MODULE  Ejecutar solo un módulo específico")
            print("  --verbose        Mostrar información detallada")
            print()
            print("Módulos disponibles: core, accounts, transactions, analytics, goals")
            print()
            print("Ejemplos:")
            print("  python test_all_endpoints.py")
            print("  python test_all_endpoints.py --url http://192.168.1.100:8000/api")
            print("  python test_all_endpoints.py --module core")
            print("  python test_all_endpoints.py --timeout 60 --verbose")
            sys.exit(0)
        
        elif sys.argv[1] == "--url" and len(sys.argv) > 2:
            BASE_URL = sys.argv[2]
            print(f"🌐 URL personalizada: {BASE_URL}")
        
        elif sys.argv[1] == "--timeout" and len(sys.argv) > 2:
            TEST_CONFIG['timeout'] = int(sys.argv[2])
            print(f"⏰ Timeout configurado: {TEST_CONFIG['timeout']} segundos")
        
        elif sys.argv[1] == "--module" and len(sys.argv) > 2:
            module_name = sys.argv[2].lower()
            
            if module_name == "core":
                print(f"🎯 Ejecutando solo módulo CORE")
                core_results = test_core_module()
                generate_module_report("CORE", core_results)
            elif module_name == "accounts":
                print(f"🎯 Ejecutando solo módulo ACCOUNTS")
                accounts_results = test_accounts_module()
                generate_module_report("ACCOUNTS", accounts_results)
            elif module_name == "transactions":
                print(f"🎯 Ejecutando solo módulo TRANSACTIONS")
                transactions_results = test_transactions_module()
                generate_module_report("TRANSACTIONS", transactions_results)
            elif module_name == "analytics":
                print(f"🎯 Ejecutando solo módulo ANALYTICS")
                analytics_results = test_analytics_module()
                generate_module_report("ANALYTICS", analytics_results)
            elif module_name == "goals":
                print(f"🎯 Ejecutando solo módulo GOALS")
                goals_results = test_goals_module()
                generate_module_report("GOALS", goals_results)
            else:
                print_error(f"Módulo desconocido: {module_name}")
                print("Módulos disponibles: core, accounts, transactions, analytics, goals")
                sys.exit(1)
            sys.exit(0)
        
        elif sys.argv[1] == "--verbose":
            print("🔍 Modo verbose activado")
            # Se puede implementar más logging detallado
        
        elif sys.argv[1] == "--no-cleanup":
            print("🚫 Modo no-cleanup - Los recursos creados no se eliminarán")
            TEST_CONFIG['cleanup'] = False
    
    try:
        # Verificar conectividad inicial
        print_info(f"Verificando conectividad con {BASE_URL}...")
        
        # Test básico de conectividad (sin autenticación)
        test_response = make_request("GET", "/", auth_required=False)
        if test_response is None:
            print_error("❌ No se puede conectar al servidor")
            print_error("Verificar que:")
            print_error("  • El servidor Django esté ejecutándose")
            print_error("  • La URL base sea correcta")
            print_error("  • No haya problemas de red/firewall")
            sys.exit(1)
        
        print_success(f"✅ Conectividad establecida")
        
        # Ejecutar todos los tests
        final_results = run_all_tests()
        
        # Cleanup opcional de recursos creados
        if TEST_CONFIG.get('cleanup', True):
            cleanup_test_resources()
        
        # Exit code basado en resultados
        if final_results['total_failed'] == 0:
            print(f"\n{Colors.GREEN}🎉 Todos los tests completados exitosamente!{Colors.END}")
            sys.exit(0)
        elif final_results['total_passed'] > final_results['total_failed']:
            print(f"\n{Colors.YELLOW}⚠️ Tests completados con algunas fallas.{Colors.END}")
            sys.exit(1)
        else:
            print(f"\n{Colors.RED}❌ Tests completados con múltiples fallas críticas.{Colors.END}")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Testing interrumpido por el usuario{Colors.END}")
        cleanup_test_resources()
        sys.exit(130)
        
    except Exception as e:
        print_error(f"Error crítico durante el testing: {str(e)}")
        cleanup_test_resources()
        sys.exit(1)

# =============================================================================
# 🔧 FUNCIONES AUXILIARES ADICIONALES
# =============================================================================

def test_endpoint_with_pagination(endpoint, description=""):
    """Prueba endpoint con soporte de paginación"""
    print_test(endpoint, "GET", f"{description} (con paginación)")
    
    # Test página 1
    response = make_request("GET", endpoint, params={"page": 1, "page_size": 5})
    data = validate_response(response, 200, endpoint)
    
    if not data:
        return False
    
    # Verificar estructura de paginación
    if isinstance(data, dict) and 'results' in data:
        print_info(f"Paginación detectada - Total: {data.get('count', 'N/A')}")
        return True
    elif isinstance(data, list):
        print_info(f"Lista simple - {len(data)} elementos")
        return True
    
    return False

def test_endpoint_filters(endpoint, filters, description=""):
    """Prueba múltiples filtros en un endpoint"""
    print_test(endpoint, "GET", f"{description} (con filtros)")
    
    results = []
    
    for filter_name, filter_value in filters.items():
        try:
            response = make_request("GET", endpoint, params={filter_name: filter_value})
            if response and response.status_code == 200:
                results.append(f"✅ Filtro {filter_name}={filter_value}")
            else:
                results.append(f"❌ Filtro {filter_name}={filter_value}")
        except:
            results.append(f"❌ Error filtro {filter_name}={filter_value}")
    
    return results

def validate_jwt_token():
    """Valida que el token JWT esté funcionando correctamente"""
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        return False
    
    # Probar endpoint que requiere autenticación
    response = make_request("GET", "/auth/profile/")
    return response is not None and response.status_code == 200

def test_crud_operations(endpoint, create_data, update_data, entity_name="recurso"):
    """Prueba operaciones CRUD completas en un endpoint"""
    results = {
        'create': False,
        'read': False,
        'update': False,
        'delete': False,
        'created_id': None
    }
    
    # CREATE
    print_test(endpoint, "POST", f"Crear {entity_name}")
    response = make_request("POST", endpoint, data=create_data)
    create_result = validate_response(response, 201, endpoint)
    
    if create_result and create_result.get('id'):
        results['create'] = True
        results['created_id'] = create_result['id']
        print_success(f"✅ {entity_name} creado - ID: {results['created_id']}")
        
        # READ
        print_test(f"{endpoint}{results['created_id']}/", "GET", f"Leer {entity_name}")
        response = make_request("GET", f"{endpoint}{results['created_id']}/")
        read_result = validate_response(response, 200, f"{endpoint}{results['created_id']}/")
        
        if read_result:
            results['read'] = True
            print_success(f"✅ {entity_name} leído correctamente")
            
            # UPDATE
            print_test(f"{endpoint}{results['created_id']}/", "PATCH", f"Actualizar {entity_name}")
            response = make_request("PATCH", f"{endpoint}{results['created_id']}/", data=update_data)
            update_result = validate_response(response, 200, f"{endpoint}{results['created_id']}/")
            
            if update_result:
                results['update'] = True
                print_success(f"✅ {entity_name} actualizado correctamente")
            
            # DELETE
            print_test(f"{endpoint}{results['created_id']}/", "DELETE", f"Eliminar {entity_name}")
            response = make_request("DELETE", f"{endpoint}{results['created_id']}/")
            
            if response and response.status_code == 204:
                results['delete'] = True
                print_success(f"✅ {entity_name} eliminado correctamente")
            else:
                print_error(f"❌ Error eliminando {entity_name}")
        else:
            print_error(f"❌ Error leyendo {entity_name}")
    else:
        print_error(f"❌ Error creando {entity_name}")
    
    return results

def performance_test(endpoint, iterations=5, description=""):
    """Realiza test básico de rendimiento en un endpoint"""
    print_test(endpoint, "GET", f"Test de rendimiento ({iterations} iteraciones)")
    
    times = []
    successful_requests = 0
    
    for i in range(iterations):
        start_time = time.time()
        response = make_request("GET", endpoint)
        end_time = time.time()
        
        request_time = end_time - start_time
        times.append(request_time)
        
        if response and response.status_code == 200:
            successful_requests += 1
        
        time.sleep(0.1)  # Pequeña pausa entre requests
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print_info(f"📈 Rendimiento: {successful_requests}/{iterations} exitosos")
        print_info(f"⏱️ Tiempo promedio: {avg_time:.3f}s (min: {min_time:.3f}s, max: {max_time:.3f}s)")
        
        return {
            'success_rate': successful_requests / iterations,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time
        }
    
    return None

def export_test_report(results, filename=None):
    """Exporta el reporte de testing a un archivo JSON"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fintrack_test_report_{timestamp}.json"
    
    try:
        # Preparar datos para JSON (convertir datetime a string)
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'base_url': BASE_URL,
            'total_tests': results['total_tests'],
            'total_passed': results['total_passed'],
            'total_failed': results['total_failed'],
            'success_rate': (results['total_passed'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0,
            'duration_seconds': (results['end_time'] - results['start_time']).total_seconds(),
            'modules': results['modules'],
            'test_config': {
                'timeout': TEST_CONFIG['timeout'],
                'max_retries': TEST_CONFIG['max_retries']
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print_success(f"📄 Reporte exportado a: {filename}")
        return filename
        
    except Exception as e:
        print_error(f"Error exportando reporte: {str(e)}")
        return None

# =============================================================================
# 🎯 TESTS ESPECIALIZADOS ADICIONALES
# =============================================================================

def test_authentication_flow():
    """Prueba completa del flujo de autenticación"""
    print_section("PRUEBA DE FLUJO DE AUTENTICACIÓN COMPLETO")
    
    results = {
        'demo_user_creation': False,
        'token_obtain': False,
        'token_usage': False,
        'token_refresh': False,
        'profile_access': False
    }
    
    # 1. Crear usuario demo
    response = make_request("POST", "/auth/demo/", auth_required=False)
    if response and response.status_code == 200:
        data = response.json()
        if data.get('access') and data.get('refresh'):
            results['demo_user_creation'] = True
            results['token_obtain'] = True
            
            # Guardar tokens temporalmente
            temp_tokens = {
                'access': data['access'],
                'refresh': data['refresh']
            }
            
            # 2. Usar token para acceder a endpoint protegido
            headers = {'Authorization': f"Bearer {temp_tokens['access']}"}
            profile_response = make_request("GET", "/auth/profile/", headers=headers, auth_required=False)
            
            if profile_response and profile_response.status_code == 200:
                results['token_usage'] = True
                results['profile_access'] = True
            
            # 3. Refrescar token
            refresh_data = {"refresh": temp_tokens['refresh']}
            refresh_response = make_request("POST", "/token/refresh/", data=refresh_data, auth_required=False)
            
            if refresh_response and refresh_response.status_code == 200:
                refresh_result = refresh_response.json()
                if refresh_result.get('access'):
                    results['token_refresh'] = True
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DEL FLUJO DE AUTENTICACIÓN:")
    for step, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {step.replace('_', ' ').title()}")
    
    success_count = sum(results.values())
    total_steps = len(results)
    
    print(f"\n🎯 Flujo de autenticación: {success_count}/{total_steps} pasos exitosos")
    
    return results

def test_data_consistency():
    """Verifica consistencia de datos entre módulos relacionados"""
    print_section("PRUEBA DE CONSISTENCIA DE DATOS")
    
    if not TEST_CONFIG.get('tokens', {}).get('access'):
        print_error("Sin autenticación - saltando pruebas de consistencia")
        return False
    
    consistency_checks = []
    
    # 1. Verificar que todas las transacciones tienen cuentas válidas
    print_test("/transactions/", "GET", "Verificando consistencia transacciones-cuentas")
    transactions_response = make_request("GET", "/transactions/")
    accounts_response = make_request("GET", "/accounts/")
    
    if transactions_response and accounts_response:
        transactions_data = transactions_response.json()
        accounts_data = accounts_response.json()
        
        # Extraer IDs de cuentas
        account_ids = set()
        accounts_list = accounts_data.get('results', accounts_data) if isinstance(accounts_data, dict) else accounts_data
        for account in accounts_list:
            account_ids.add(account['id'])
        
        # Verificar transacciones
        transactions_list = transactions_data.get('results', transactions_data) if isinstance(transactions_data, dict) else transactions_data
        invalid_transactions = []
        
        for transaction in transactions_list:
            if transaction.get('from_account') and transaction['from_account'] not in account_ids:
                invalid_transactions.append(f"Transacción {transaction['id']} - cuenta origen inválida")
            if transaction.get('to_account') and transaction['to_account'] not in account_ids:
                invalid_transactions.append(f"Transacción {transaction['id']} - cuenta destino inválida")
        
        if not invalid_transactions:
            consistency_checks.append("✅ Consistencia transacciones-cuentas: OK")
        else:
            consistency_checks.append(f"❌ Inconsistencias encontradas: {len(invalid_transactions)}")
    
    # 2. Verificar que todas las metas tienen cuentas asociadas válidas
    print_test("/goals/", "GET", "Verificando consistencia metas-cuentas")
    goals_response = make_request("GET", "/goals/")
    
    if goals_response and accounts_response:
        goals_data = goals_response.json()
        goals_list = goals_data.get('results', goals_data) if isinstance(goals_data, dict) else goals_data
        
        invalid_goals = []
        for goal in goals_list:
            if goal.get('associated_account') and goal['associated_account'] not in account_ids:
                invalid_goals.append(f"Meta {goal['id']} - cuenta asociada inválida")
        
        if not invalid_goals:
            consistency_checks.append("✅ Consistencia metas-cuentas: OK")
        else:
            consistency_checks.append(f"❌ Inconsistencias en metas: {len(invalid_goals)}")
    
    # Mostrar resultados de consistencia
    print(f"\n📊 RESULTADOS DE CONSISTENCIA:")
    for check in consistency_checks:
        print(f"  {check}")
    
    return len([c for c in consistency_checks if c.startswith("✅")]) == len(consistency_checks)

# Fin de la continuación del archivo
print("\n" + "="*80)
print("🧪 FinTrack Test Suite - Sistema de Testing Completo")
print("Desarrollado para validación automática de todos los endpoints")
print("="*80)