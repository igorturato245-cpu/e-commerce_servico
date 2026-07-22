from django.views import View
from django.http import JsonResponse
from carrinho.views.view_carrinho import _get_card_for_request
from carrinho.models import Item_carrinho
from django.shortcuts import get_object_or_404
from utils.formata_preco import oficial_formatar_preco


class removercarrinho(_get_card_for_request,View):
    def post(self,request,*args, **kwargs):
        
        item_id=request.POST.get('item_id')
        carrinho=self.get_carrinho(request)
        item=get_object_or_404(Item_carrinho.objects.select_related('produto'), id=item_id, carrinho=carrinho)
        item.delete()
        
        itens=carrinho.itens.all()#type:ignore
        subtotal=carrinho.total()
        
        itens_restantes=len(itens)
        
        merge=oficial_formatar_preco()
        
        return JsonResponse({
            'itens_restantes':itens_restantes,
            'subtotal':float(subtotal),
            'subtotal_format':merge.formata_preco(subtotal),
            'success':True
        })