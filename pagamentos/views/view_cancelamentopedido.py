from django.shortcuts import render,redirect,get_object_or_404
from pagamentos.models import Pedido,Pedidoitem
from django.views import View
from django.contrib import messages


class CancelarPedido(View):
    def get(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não está logado. Faça seu login para conseguir concluir o cancelamento')
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)
        
        if not pedido.pode_cancelar_direto:
            messages.error(request,'Pedido ja cancelado/enviado, cancelamento automatimo esta indisponivel. Tente solicitar seu reembolso mais tarde.')
        itens_pedido=Pedidoitem.objects.filter(pedido=pedido)
        
        context={
            'pedido':pedido,
            'itens':itens_pedido
        }
        
        return render(request,'pagamentos/cancelar.html',context)
    
class ConclusaCancelamento(View):
    def get(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não está logado.Faça seu login para conseguir concluir o cancelamento.')
            return redirect('cadastro_login:login')
            
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)
        
        return render(request,'pagamentos/conclusao_cancelamento.html',{'pedido':pedido})