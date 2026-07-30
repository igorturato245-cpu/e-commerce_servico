from django.views import View 
from carrinho.views.view_carrinho import _get_card_for_request
from django.shortcuts import get_object_or_404
from carrinho.models import Item_carrinho
from django.http import JsonResponse
from utils.formata_preco import oficial_formatar_preco

class quantidade_carrinho(_get_card_for_request,View):
    def post(self,request,*args, **kwargs):
        
        item_id=request.POST.get('item_id')
        
        try:
            nova_quantidade=int(request.POST.get('quantidade', 1))
        except ValueError:
            nova_quantidade=1
            
            
        carrinho=self.get_carrinho(request)
        
        item=get_object_or_404(Item_carrinho.objects.select_related('produto'), id=item_id,carrinho=carrinho)
        
        item.atualiza_qtd(nova_quantidade)
        item.save()
        
        subtotal=carrinho.total()
        
        merge=oficial_formatar_preco()
        
        return JsonResponse({
            'quantidade':item.quantidade,
            'subtotal':float(subtotal),
            'subtotal_format':merge.formata_preco(subtotal)
        })
        
        
        