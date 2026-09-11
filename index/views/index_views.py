from django.shortcuts import render
from django.views import View
from produtos.models import Product

class Indexview(View):
    def get(self, request):
        produtos_oferta=Product.objects.filter(ofertas_do_dia=True).select_related('category')
        
        return render(request, 'index.html',context={'produtos_oferta':produtos_oferta})
