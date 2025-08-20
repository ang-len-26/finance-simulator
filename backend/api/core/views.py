import os
import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from ..accounts.models import Account
from ..transactions.models import Transaction
from .models import UserProfile
from .serializers import UserRegistrationSerializer, UserProfileSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Endpoint para 'Crear Cuenta' con serializer"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({'errors': serializer.errors}, status=400)
    
    try:
        user = serializer.save()
        
        # Crear perfil de usuario
        UserProfile.objects.create(user=user)
        
        # Crear cuenta por defecto (Efectivo)
        Account.objects.create(
            user=user,
            name="Efectivo",
            account_type="cash",
            initial_balance=Decimal('0.00')
        )
        
        return Response({
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_demo_user(request):
    """Para 'Probar demo sin registrarse' - Usa el sistema completo de setup_demo"""
    
    try:
        # Generar username único para demos temporales
        demo_prefix = os.getenv('DEMO_USERNAME', 'demo_temp')
        unique_username = f"{demo_prefix}_{uuid.uuid4()}"
        
        # Crear usuario temporal
        demo_user = User.objects.create_user(
            username=unique_username,
            password='demo123',
            email=f"{unique_username}@demo.fintrack.com"
        )
        
        # Crear perfil demo con expiración
        demo_duration = int(os.getenv('DEMO_DURATION_HOURS', '24'))
        UserProfile.objects.create(
            user=demo_user,
            is_demo=True,
            demo_expires=timezone.now() + timedelta(hours=demo_duration)
        )
        
        # AQUÍ USAR EL SISTEMA EXISTENTE:
        # Importar y usar la lógica de setup_demo
        from api.core.management.commands.setup_demo import Command as SetupDemoCommand
        demo_command = SetupDemoCommand()
        demo_command.demo_user = demo_user  # Usar el usuario recién creado
        
        # Crear los datos demo completos
        demo_command.create_demo_accounts()
        demo_command.create_demo_transactions()
        demo_command.create_demo_goals()
        demo_command.update_account_balances()
        
        # Retornar tokens para acceso inmediato
        refresh = RefreshToken.for_user(demo_user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'demo_user': True,
            'username': unique_username,
            'expires_at': UserProfile.objects.get(user=demo_user).demo_expires,
            'accounts_created': Account.objects.filter(user=demo_user).count(),
            'transactions_created': Transaction.objects.filter(user=demo_user).count()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error creando usuario demo: {str(e)}'}, 
            status=500
        )

@api_view(["POST"])
def create_superuser(request):
    
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    # Validar que las variables estén configuradas
    if not all([admin_username, admin_email, admin_password]):
        return Response({
            "status": "error", 
            "message": "Variables de entorno requeridas: ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD"
        }, status=500)
    
    try:
        if User.objects.filter(username=admin_username).exists():
            return Response({
                "status": "error", 
                "message": f"Admin user '{admin_username}' already exists"
            }, status=400)

        user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        
        # Crear perfil para el admin
        UserProfile.objects.create(user=user)
        
        return Response({
            "status": "success", 
            "message": f"Superuser '{admin_username}' created successfully"
        }, status=201)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
def run_migrations(request):
    """Endpoint para ejecutar migraciones manualmente"""
    try:
        call_command('migrate')
        return Response({"status": "success", "message": "Migrations applied successfully"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})

@api_view(['GET'])
def user_profile(request):
    """Endpoint para obtener perfil del usuario autenticado"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Crear perfil si no existe
        profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
