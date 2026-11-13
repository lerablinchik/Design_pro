from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Application


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Управление категориями заявок (Добавление, удаление, редактирование)"""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Панель управления заявками для Администратора"""
    list_display = ('title', 'photo_preview', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('photo_preview',) #картинку редачить нельзя ток смотретть

    # Добавляем быстрые действия (Actions) для смены статусов одной кнопкой
    actions = ['make_processing', 'make_completed']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'category', 'photo', 'photo_preview')
        }),
        ('Обработка заявки (Для администратора)', {
            'fields': ('status', 'comment', 'design_photo')
        }),
    )

    def photo_preview(self, obj):
        """Отображение миниатюры прикрепленного плана в списке и карточке заявки"""
        if obj.photo:
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" style="width: 70px; height: 50px; object-fit: cover; border-radius: 4px;" /></a>',
                obj.photo.url
            )
        return "Нет фото"
    photo_preview.short_description = "План / Фото"

    def make_processing(self, request, queryset):
        """Быстрое действие: Принять в работу"""
        queryset.update(status='w')

    make_processing.short_description = "Перевести выбранные заявки в статус «В работе»"

    def make_completed(self, request, queryset):
        """Быстрое действие: Выполнено"""
        queryset.update(status='d')

    make_completed.short_description = "Перевести выбранные заявки в статус «Выполнено»"
