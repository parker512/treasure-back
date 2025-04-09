from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Поля, которые будут отображаться в списке пользователей
    list_display = ('email', 'first_name', 'last_name', 'get_password', 'is_staff', 'is_active')
    
    # Поля, доступные для поиска
    search_fields = ('email', 'first_name', 'last_name')
    
    # Фильтры в боковой панели
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    
    # Поля в форме редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'birth_date', 'region', 'city', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Поля в форме создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    # Метод для отображения хешированного пароля
    def get_password(self, obj):
        return obj.password
    
    get_password.short_description = 'Password (hashed)'
    
    # Указываем поле для сортировки (email вместо username)
    ordering = ('email',)

# Регистрация модели с кастомной админкой
admin.site.register(CustomUser, CustomUserAdmin)