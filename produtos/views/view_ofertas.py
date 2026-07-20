from django.shortcuts import render
from django.views import View
from produtos.models import Product


class ofertas_do_dia(View):
    def get(self,request):
        ofertas_dia=Product.objects.filter(ofertas_do_dia=True,disponivel=True).select_related('category')
        
        context={
            "ofertas_do_dia":ofertas_dia
        }        
        
        return render(request,'ofertas_dia.html', context)