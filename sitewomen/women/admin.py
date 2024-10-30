from django.contrib import admin, messages
from django.db.models.functions import Length

from .models import Women, Category


# Register your models here.

class MarriedFilter(admin.SimpleListFilter):
    title = 'Статус женщин'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('married', 'Замужем'),
            ('single', 'Не замужем'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'married':
            return queryset.filter(husband__isnull=False)
        elif self.value() == 'single':
            return queryset.filter(husband__isnull=True)
        return queryset


@admin.register(Women)
class WomenAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'content', 'cat', 'husband', 'tags'] # список отображаемых полей при редактировании записи в админ-панели
    #exclude = ['tags', 'is_published'] # список исключаемых полей при редактировании записи в админ-панели
    #readonly_fields = ['slug'] # список полей, доступных только для просмотра, при редактировании записи в админ-панели
    prepopulated_fields = {'slug': ('title', )}  # автозаполнение на основе других полей
    filter_horizontal = ['tags'] # виджет расширенный горизонтальный
    #filter_vertical = ['tags'] # виджет расширенный вертикальный
    list_display = ('title', 'time_create', 'is_published', 'cat', 'brief_info')
    list_display_links = ('title',)
    ordering = ['time_create', 'title']
    list_editable = ('is_published',) # список редактируемых полей модели в админ-панели
    list_per_page = 10 # число отображаемых записей на странице в админ-панели
    actions = ['set_published', 'set_draft'] # список пользовательских действий
    search_fields = ['title__startswith', 'cat__name'] #список полей, по которым осуществляется поиск в админ-панели
    list_filter = [MarriedFilter, 'cat__name', 'is_published'] # список полей для фильтрации записей в админ-панели

    @admin.display(description='Краткое описание', ordering=Length('content'))
    def brief_info(self, women: Women):
        return f'Описание {len(women.content)} символов.'

    @admin.action(description='Опубликовать выбранные записи')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Women.Status.PUBLISHED)
        self.message_user(request, f'Изменено {count} записей')

    @admin.action(description='Снять с публикации выбранные записи')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Women.Status.DRAFT)
        self.message_user(request, f'{count} записей снято с публикации!', messages.WARNING)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
