from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
	path('api/', include('api.core.urls')),
    path('api/', include('api.accounts.urls')),
    path('api/', include('api.transactions.urls')),
    path('api/', include('api.analytics.urls')),
    path('api/', include('api.goals.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
