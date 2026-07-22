from django.urls import path
from carrinho.views import view_carrinho,view_add_carrinho,view_qtd_carrinho,view_remover_carrinho


app_name='carrinho'

urlpatterns = [
    path('cart/',view_carrinho.carrinho.as_view(),name='carrinho_url'),
    path('adicionar/<int:produto_id>/',view_add_carrinho.adicionar_ao_carrinho.as_view(),name='add_ao_carrinho'),
    path('quantidade/',view_qtd_carrinho.quantidade_carrinho.as_view(),name='qtd_no_carrinho'),
    path('remover/',view_remover_carrinho.removercarrinho.as_view(),name='remover_do_carrinho')
]
