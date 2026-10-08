import logging
from produtos.models import Product
from carrinho.views.view_carrinho import _get_card_for_request
from django.shortcuts import get_object_or_404,redirect
from carrinho.models import Item_carrinho
from django.contrib import messages
from django.views import View
from index.meta_capi import EnviaEvento


class adicionar_ao_carrinho(_get_card_for_request,View):
    def post(self,request, produto_id,*args, **kwargs):
        produto=get_object_or_404(Product, id=produto_id)
        carrinho=self.get_carrinho(request)
        
        try:
            quantidade_add=int(request.POST.get('quantidade',1))
        except:
            quantidade_add=1
            
        email_usuario=request.user.email if request.user.is_authenticated else None
        
        item,create=Item_carrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={
                'quantidade':0,
                'preco_unitario':produto.get_preco()
            }
        )
        
        quantidade_total=item.quantidade + quantidade_add
                
                
        item.atualiza_qtd(quantidade_total)
        item.save()
            
        obj=EnviaEvento()
        obj.enviar_evento_data(
            request=request,
            event_name='AddToCart',
            user_email=email_usuario,
            custom_data={
                'currency':'BRL',
                'value':float(carrinho.total()),
                'num_items':carrinho.itens.count(),#type:ignore
                'content_ids':[str(produto.pk)],
                'content_type':'product'
            }
        )
        
        if create:
            messages.success(request,f'Sucesso ao adicionar o produto {produto.name} ao carrinho.')
        else:          
            messages.success(request, f'Quantidade do produto {produto.name} atualizada no carrinho.')
            
        acao=request.POST.get('acao')
        
        if acao == 'comprar':
            return redirect('carrinho:carrinho_url')
        return redirect('index:index')
                
            
            
        