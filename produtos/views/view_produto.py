from django.shortcuts import render,get_object_or_404
from django.views import View
from produtos.models import Product

class Produto(View):
    def get(self,request,categoria_slug, produto_slug):
        single_produtct=get_object_or_404(Product.objects.select_related('category'),slug=produto_slug,category__slug=categoria_slug,disponivel=True)
        ofertas_do_dia=Product.objects.filter(ofertas_do_dia=True,disponivel=True ).select_related('category')
        
        context={
            'produto':single_produtct,
            'ofertas_dia':ofertas_do_dia
        }
        
        return render(request,'produto_detalhe.html',context)