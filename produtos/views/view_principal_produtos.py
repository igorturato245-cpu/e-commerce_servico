from django.shortcuts import get_object_or_404, render
from django.views import View

from produtos.models import Avaliation_product, Category, Product


class products(View):
    def get(self,request,categoria_slug):
        categoria=get_object_or_404(Category,slug=categoria_slug)
        produtos=Product.objects.filter(category=categoria).select_related('category')
        avaliacoes=Avaliation_product.objects.filter(produto__in=produtos).select_related('produto')
        
        context={
            'produtos':produtos,
            'categorias':categoria,
            'avaliacao_produto':avaliacoes            
        }
        
        return render(request,'produto.html', context)