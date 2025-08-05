from django.db import models
from django.contrib.auth.models import User

# =====================================================
# MODELO DE USUARIO PARA DEMO Y REGISTRO
# =====================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_demo = models.BooleanField(default=False)
    demo_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Demo: {self.is_demo}"
