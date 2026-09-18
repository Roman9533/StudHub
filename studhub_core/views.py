from django.shortcuts import render, redirect
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Material
from .forms import MaterialUploadForm
from .models import User, Discipline, Material, MaterialRating
from .serializers import UserSerializer, DisciplineSerializer, MaterialSerializer, RatingSerializer
from .permissions import IsModeratorOrAuthorReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['semester', 'faculty']
    search_fields = ['title', 'lecturer']


class MaterialViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsModeratorOrAuthorReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['material_type', 'discipline', 'is_verified']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """Оптимизация БД-запросов с предзагрузкой связей для диплома"""
        return Material.objects.select_related('author', 'discipline').prefetch_related('ratings').all()

    def perform_create(self, serializer):
        # Автоматически назначаем текущего авторизованного студента автором
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Кастомный эндпоинт для оценки материала / отправки жалобы"""
        material = self.get_object()
        user = request.user
        
        # Обновляем оценку, если она уже существует, или создаем новую (Upsert)
        rating, created = MaterialRating.objects.update_or_create(
            material=material,
            user=user,
            defaults={
                'is_upvote': request.data.get('is_upvote', True),
                'report_reason': request.data.get('report_reason', '')
            }
        )
        
        # Если отправлена жалоба с текстом, автоматически снимаем верификацию материала
        if rating.report_reason:
            material.is_verified = False
            material.save()

        return Response({'status': 'Оценка успешно сохранена'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def track_click(self, request, pk=None):
        """Инкремент счетчика скачиваний при клике на ресурс"""
        material = self.get_object()
        material.download_count += 1
        material.save(update_fields=['download_count'])
        return Response({'download_count': material.download_count}, status=status.HTTP_200_OK)


    # ... предыдущий код ViewSets ...

def home_page(request):
    search_query = request.GET.get('search', '')
    
    # Обработка загрузки данных пользователем
    if request.method == 'POST':
        form = MaterialUploadForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            # Если пользователь авторизован — привязываем его как автора
            if request.user.is_authenticated:
                material.author = request.user
            # ВАЖНО: Новые файлы от студентов уходят на премодерацию (is_verified = False)
            material.is_verified = False 
            material.save()
            return redirect('/') # Перезагружаем страницу после успешной отправки
    else:
        form = MaterialUploadForm()
        
    # Базовый запрос для вывода карточек
    materials_queryset = Material.objects.filter(is_verified=True).select_related('discipline')
    if search_query:
        materials_queryset = materials_queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        
    context = {
        'materials': materials_queryset[:6],
        'search_query': search_query,
        'upload_form': form # Отправляем форму на сайт
    }
    return render(request, 'index.html', context)




    

    

