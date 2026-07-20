from django.contrib import admin
from .models import *

class CarrosselImg(admin.TabularInline):
    model=ProdutoImagem
    extra=1

@admin.register(Category)
class Categoryadmin(admin.ModelAdmin):
    list_display='name','slug',
    prepopulated_fields={'slug':('name',)}
    ordering=('-id',)

@admin.register(Product)
class Productadmin(admin.ModelAdmin):
    list_display=('name','preco','category','ofertas_do_dia')
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200
    list_display_links=('name',)
    prepopulated_fields={'slug':('name',)}
    inlines=[
        CarrosselImg
    ]
    
@admin.register(Avaliation_product)
class Avaliationadmin(admin.ModelAdmin):
    list_display='nota_site','nota_produto'
    
@admin.register(Token_Fonecedor)
class TokenFornecedoradmin(admin.ModelAdmin):
    list_display='access_token','refresh_token'
    