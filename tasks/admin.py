from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'id',
        'status',
        'assigned_to',
        'created_by',
        'created_at',
        'updated_at',
    )

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'description',
                'priority',
                'status',
                'assigned_to',
                'created_by',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


