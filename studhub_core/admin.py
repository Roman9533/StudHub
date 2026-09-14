from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Discipline, Material, MaterialRating

# Красиво регистрируем модель пользователя
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'university', 'faculty', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Данные вуза', {'fields': ('role', 'university', 'faculty', 'course')}),
    )

# Регистрируем дисциплины
@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('title', 'semester', 'faculty', 'lecturer')
    list_filter = ('semester', 'faculty')
    search_fields = ('title', 'lecturer')

# Регистрируем учебные материалы
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'material_type', 'discipline', 'author', 'is_verified', 'download_count')
    list_filter = ('material_type', 'is_verified', 'discipline')
    search_fields = ('title', 'description')
    actions = ['approve_materials']

    @admin.action(description='Утвердить выбранные материалы')
    def approve_materials(self, request, queryset):
        queryset.update(is_verified=True)

# Регистрируем оценки и жалобы
@admin.register(MaterialRating)
class MaterialRatingAdmin(admin.ModelAdmin):
    list_display = ('material', 'user', 'is_upvote', 'report_reason')
    list_filter = ('is_upvote',)
