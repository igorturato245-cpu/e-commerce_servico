from django.shortcuts import render,redirect,get_object_or_404
from pagamentos.models import Pedido,Solicitacao_reembolso
from django.views import View
from django.contrib import messages


class SolicitarReembolso(View):
    def post(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não logado. Faça seu login para conseguir concluir a ação de reembolso.')
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)
        
        if not pedido.pode_solicitar_reembolso:
            messages.error(request, 'Usuario não pode solicitar reembolso, prazo de solicitação de reembolso estourado.')
            
        ja_reembolsou=Solicitacao_reembolso.objects.filter(pedido=pedido).exists()
        
        if ja_reembolsou:
            messages.error(request, 'Usuario já recebeu o reembolso.')
            return redirect('index:index')
        
        motivo=request.POST.get('motivo_devolucao')
        feedback=request.POST.get('feedback-devolucao')
        evidencias=request.FILES.get('evidencias-reembolso')
        
        Solicitacao_reembolso.objects.create(
            pedido=pedido,
            motivo=motivo,
            feedback=feedback,
            evidencias=evidencias,
            status='pending',
        )
        
        messages.success(request,'Solicitação de cancelamento/reembolso enviada com sucesso. Aguarde nosso contato. ')
        return redirect('pagamentos:meus_pedidos')
    
    
class AnaliseReembolso(View):
    def get(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não logado.Faça seu login para conseguir acompanhar a sua solicitação de reembolso.')
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)        
        solicitacao=Solicitacao_reembolso.objects.filter(pedido=pedido).first()
        
        if not solicitacao:
            messages.error(request,'Não é possivel solicitar o reembolso, prazo de solicitação de reembolso foi estourado.')
            return redirect('pagamentos:meus_pedidos') 
        
        context={
            'pedido':pedido,
            'solicitacao':solicitacao
        }
    
    
        return render(request,'pagamentos/analise_reembolso.html',context)
    
        