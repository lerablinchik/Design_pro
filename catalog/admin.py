from django.contrib import admin
from .models import Category, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями заявок (Добавление, удаление, редактирование)"""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Панель управления заявками для Администратора"""
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description')

    # Добавляем быстрые действия (Actions) для смены статусов одной кнопкой
    actions = ['make_processing', 'make_completed']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'category', 'photo')
        }),
        ('Обработка заявки (Для администратора)', {
            'fields': ('status', 'comment', 'design_photo')
        }),
    )

    def make_processing(self, request, queryset):
        """Быстрое действие: Принять в работу"""
        queryset.update(status='w')

    make_processing.short_description = "Перевести выбранные заявки в статус «В работе»"

    def make_completed(self, request, queryset):
        """Быстрое действие: Выполнено"""
        queryset.update(status='d')

    make_completed.short_description = "Перевести выбранные заявки в статус «Выполнено»"
