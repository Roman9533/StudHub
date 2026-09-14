from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, DisciplineViewSet, MaterialViewSet

# Инициализация REST-роутера
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'disciplines', DisciplineViewSet, basename='discipline')
router.register(r'materials', MaterialViewSet, basename='material')

urlpatterns = [
    # Главные системные роуты API (CRUD операции)
    path('v1/', include(router.urls)),
    
    # JWT-Аутентификация для сессий студентов
    path('v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
