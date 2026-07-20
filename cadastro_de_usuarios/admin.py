from django.contrib import admin
from cadastro_de_usuarios.models import *

@admin.register(Perfil)
class Perfil_admin(admin.ModelAdmin):
    pass

@admin.register(Endereco_usuario)
class Endereco_admin(admin.ModelAdmin):
    pass