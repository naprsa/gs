from django.contrib import admin
from .models import PrintLayout

# Register your models here.


@admin.register(PrintLayout)
class PrintLayoutAdmin(admin.ModelAdmin):
    pass
