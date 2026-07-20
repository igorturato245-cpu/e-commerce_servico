from django.urls import path
from produtos.views import view_principal_produtos,view_ofertas,view_produto

app_name = 'produtos'

urlpatterns = [
    path('ofertas-do-dia/',view_ofertas.ofertas_do_dia.as_view(),name='ofertas'),
    path('<slug:categoria_slug>/',view_principal_produtos.products.as_view(),name='produto'),
    path('<slug:categoria_slug>/<slug:produto_slug>/',view_produto.Produto.as_view(),name='detalhe_produto')
]
