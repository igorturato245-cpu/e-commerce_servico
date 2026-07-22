from django.contrib import admin
from carrinho import models


@admin.register(models.Carrinho)
class Carrinhoadmin(admin.ModelAdmin):
    list_display=('id','criado_em',)
    ordering=('-id',)
    list_filter=('criado_em',)


@admin.register(models.Item_carrinho)
class Itemcarrinhoadmin(admin.ModelAdmin):
    list_display=('id','carrinho','produto','quantidade',)
    ordering=('-id',)
    list_filter=('carrinho','produto',)
