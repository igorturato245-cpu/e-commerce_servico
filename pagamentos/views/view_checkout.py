from django.shortcuts import render,redirect
from cadastro_de_usuarios.models import Endereco_usuario
from carrinho.views.view_carrinho import _get_card_for_request
from django.contrib import messages
from pagamentos.models import Pedido
from django.views import View


class Checkout(View):
    def post(self,request):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não está logado. Conclua seu login ou crie seu cadastro e conclua sua compra.')
            return redirect('cadastro_login:login')
        
        endereco=Endereco_usuario.objects.filter(usuario=request.user,padrao=True).first() or \
            Endereco_usuario.objects.filter(usuario=request.user).first()
            
        get_cart=_get_card_for_request()
        carrinho=get_cart.get_carrinho(request)
        
        if not carrinho or not carrinho.itens.exists():#type:ignore
            messages.error(request,'Carrinho vazio.')
            return redirect('carrinho:carrinho_url')
        
        if not endereco:
            messages.error(request,'Necessario endereço para concluir a compra.')
            return redirect('cadastro_login:criar_end')
        
        itens=carrinho.itens.select_related('produto').all()#type:ignore
        
        itens_para_frete=[]
        
        for item in itens:
            itens_para_frete.append({
                'id':item.produto.erp_id or str(item.produto.id),
                'quantity':item.quantidade
            })
            
        calcular_frete=Pedido.calcula_total(endereco.cep,itens_para_frete,carrinho.total())
        
        
        request.session['frete_calculado']=str(calcular_frete['valor_frete'])
        
        context={
            'itens':itens,
            'valor_frete':calcular_frete['valor_frete'],
            'prazo':calcular_frete['prazo_entrega'],
            'subtotal':calcular_frete['total_produtos'],
            'total_com_frete':calcular_frete['total_com_frete'],
            'endereco':[endereco],
            'cart':carrinho,
        }
        
        
        return render(request,'pagamentos/checkout.html',context)
    
            