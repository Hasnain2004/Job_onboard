from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Job, Application, ContactSupport

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'username')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'username', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'created_by', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')

class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant_name', 'job', 'applicant_email', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('applicant_name', 'applicant_email', 'job__title')
    readonly_fields = ('applied_at', 'updated_at')

class ContactSupportAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(ContactSupport, ContactSupportAdmin)
