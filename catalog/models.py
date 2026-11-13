import uuid
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Модель категорий заявок (например, 3D-дизайн, 2D-дизайн, Эскиз)"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Название категории") #unique=True запрещает 2 одинаковых категории делать

    class Meta:
        verbose_name = "Категория заявки"
        verbose_name_plural = "Категории заявок"

    def __str__(self): #без этого будет просто: Category object (1), а не 3д дизайн
        return self.name


class Application(models.Model):
    """Модель заявки на разработку дизайна интерьера помещения"""
    STATUS_CHOICES = (
        ('n', 'Новая'),
        ('w', 'Принято в работу'),
        ('d', 'Выполнено'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Уникальный ID заявки")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Заявитель")
            #один ко многим, у 1 чел много заявок,
            #on_delete=models.CASCADE: если удалить пользователя из базы, все его заявки удалятс
    title = models.CharField(max_length=200, verbose_name="Название") # чар для короткого
    description = models.TextField(verbose_name="Описание") # текст для длинного
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория") #связь с таблицей категорий

    # Поля под изображения (план помещения и итоговый дизайн)
    photo = models.ImageField(upload_to='plans/', verbose_name="Фото помещения или его план") #поле для загрузки картинки
    design_photo = models.ImageField(upload_to='designs/', null=True, blank=True, verbose_name="Итоговый дизайн")
            #картинка готового дизайна от админа
            #null = True, blank = True: необязат поле при создании заявки, админ потом может прикрепить

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Временная метка добавления")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n', verbose_name="Статус заявки")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий администратора")
            #auto_now_add = True: записывает текущее время в момент создания заявки
    class Meta:
        ordering = ['-created_at']  # свежие заявки выводятся в начале списка по умолчанию
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
            #get_status_display:  превращает букву 'n' в слово "Новая"
