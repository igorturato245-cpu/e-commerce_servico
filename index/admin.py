from django.contrib import admin
from .models import Contato

@admin.register(Contato)
class adminContato(admin.ModelAdmin):
    pass