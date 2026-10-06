from django.contrib import admin
from .models import Pedido,Pedidoitem,Solicitacao_reembolso,Cupons

class PedidoitemTabular(admin.TabularInline):
    model=Pedidoitem
    extra=1

@admin.register(Pedido)
class Pedidoadmin(admin.ModelAdmin):
    list_display=('id','usuario','status','payment_reference','erp_order_id','erp_status',)
    list_display_links=('id','usuario',)
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200
    inlines=[
        PedidoitemTabular,
        ]


@admin.register(Pedidoitem)
class Pedidoitemadmin(admin.ModelAdmin):
    pass


@admin.register(Solicitacao_reembolso)
class Soliciacao_reemboladmin(admin.ModelAdmin):
    list_display=('id','pedido','motivo','status')
    list_display_links=('id','pedido',)
    ordering=('-id',)
    list_per_page=10
    list_max_show_all=200
    
    
@admin.register(Cupons)
class Cupons_admin(admin.ModelAdmin):
    pass