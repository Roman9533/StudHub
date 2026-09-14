from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Кастомная модель пользователя вуза с ролевой моделью"""
    class Roles(models.TextChoices):
        STUDENT = 'ST', 'Студент'
        STAROSTA = 'SR', 'Староста'
        MODERATOR = 'MD', 'Модератор'

    role = models.CharField(
        max_length=2, 
        choices=Roles.choices, 
        default=Roles.STUDENT,
        verbose_name="Роль в системе"
    )
    university = models.CharField(max_length=150, verbose_name="Вуз", blank=True)
    faculty = models.CharField(max_length=150, verbose_name="Факультет", blank=True)
    course = models.PositiveSmallIntegerField(
        verbose_name="Курс", 
        validators=[MinValueValidator(1), MaxValueValidator(6)], 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Discipline(models.Model):
    """Модель учебной дисциплины (предмета)"""
    title = models.CharField(max_length=255, verbose_name="Название дисциплины")
    semester = models.PositiveSmallIntegerField(verbose_name="Семестр")
    lecturer = models.CharField(max_length=150, verbose_name="Преподаватель", blank=True)
    faculty = models.CharField(max_length=150, verbose_name="Факультет/Кафедра")

    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.faculty}, семестр {self.semester})"


class Material(models.Model):
    """Модель агрегируемого учебного материала (файл или веб-ссылка)"""
    class MaterialTypes(models.TextChoices):
        LECTURE = 'LEC', 'Лекция'
        PRACTICE = 'PRC', 'Практика/Семинар'
        LABORATORY = 'LAB', 'Лабораторная работа'
        EXAM = 'EXM', 'Материалы к экзамену'
        USEFUL_LINK = 'LNK', 'Полезная ссылка'

    title = models.CharField(max_length=255, verbose_name="Заголовок материала")
    description = models.TextField(verbose_name="Описание контента", blank=True)
    material_type = models.CharField(
        max_length=3, 
        choices=MaterialTypes.choices, 
        default=MaterialTypes.LECTURE,
        verbose_name="Тип материала"
    )
    
    # Поля для хранения ресурсов (допускается загрузка файла ИЛИ прикрепление внешней ссылки)
    file_attachment = models.FileField(upload_to='materials/%Y/%m/', verbose_name="Файл", blank=True, null=True)
    external_url = models.URLField(verbose_name="Внешняя ссылка", blank=True, null=True)
    
    discipline = models.ForeignKey(
        Discipline, 
        on_delete=models.CASCADE, 
        related_name='materials', 
        verbose_name="Дисциплина"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='uploaded_materials',
        verbose_name="Автор"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Количество скачиваний/переходов")
    is_verified = models.BooleanField(default=False, verbose_name="Проверено модератором")

    class Meta:
        verbose_name = "Учебный материал"
        verbose_name_plural = "Учебные материалы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MaterialRating(models.Model):
    """Система краудсорсинговой оценки качества и актуальности материалов"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    is_upvote = models.BooleanField(verbose_name="Положительная оценка (Лайк)")
    report_reason = models.TextField(verbose_name="Жалоба на неактуальность/спам", blank=True, null=True)

    class Meta:
        verbose_name = "Оценка материала"
        verbose_name_plural = "Оценки материалов"
        unique_together = ('material', 'user')  # Ограничение: 1 голос от 1 пользователя на 1 материал
