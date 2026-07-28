from django.shortcuts import render,redirect,get_object_or_404
from pagamentos.models import Pedido,Pedidoitem
from django.views import View
from django.contrib import messages

class MeusPedidos(View):
    def get(self,request):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não esta logado. Faça seu login para acessar seus pedidos.')
            return redirect('cadastro_login:login')
        
        pedido=Pedido.objects.filter(usuario=request.user).order_by('-created_at')
        
        context={
            'pedidos':pedido
        }
        
        return render(request,'pagamentos/meus_pedidos.html',context)
    
    
    
class DetalhePedido(View):
    def get(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não esta logado. Faça seu login para acessar seus pedidos.')
            return redirect('cadastro_login:login')            
            
        pedido=get_object_or_404(Pedido,usuario=request.user,pk=pedido_id)
        
        #itens_pedido=Pedidoitem.objects.filter(pedido=pedido)
        
        itens_pedido=Pedidoitem.objects.select_related('produto').filter(pedido=pedido)
        
        
        context={
            'pedido':pedido,
            'itens':itens_pedido
        }
        
        return render(request,'pagamentos/detalhe_pedido.html',context)