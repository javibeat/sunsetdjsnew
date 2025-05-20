from django.contrib import admin
from .models import DJ, Shift

@admin.register(DJ)
class DJAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time', 'dj')
    list_filter = ('date', 'dj')
    search_fields = ('title',)
