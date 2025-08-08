from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# =====================================================
# MODELO DE USUARIO PARA DEMO Y REGISTRO
# =====================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_demo = models.BooleanField(default=False)
    demo_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"{self.user.username} - Demo: {self.is_demo}"
    
    @property
    def is_demo_expired(self):
        """Verifica si el usuario demo ha expirado"""
        if not self.is_demo or not self.demo_expires:
            return False
        return timezone.now() > self.demo_expires
    
    def get_account_count(self):
        """Retorna el número de cuentas del usuario"""
        from ..accounts.models import Account
        return Account.objects.filter(user=self.user).count()
    
    def get_transaction_count(self):
        """Retorna el número de transacciones del usuario"""
        from ..transactions.models import Transaction
        return Transaction.objects.filter(user=self.user).count()