from django.shortcuts import render,get_object_or_404
from django.views import View
from index.meta_capi import EnviaEvento
from pagamentos.models import Pedido
from cadastro_de_usuarios.models import Endereco_usuario,Perfil


class RetornoPagamento(View):
    def get(self,request):
        reference=request.GET.get('reference')
        status=request.GET.get('status','pending')
        sucesso=status in ['3','paid']
        
        pedido=None
        if reference:
            pedido=Pedido.objects.filter(payment_reference=reference).first()
            
        if not pedido and request.user.is_authenticated:
            pedido=Pedido.objects.filter(usuario=request.user).order_by('-created_at').first()
        
        context={
            'reference':reference,
            'status':status,
            'success':sucesso,
            'pedido':pedido
        }
        
        if sucesso and pedido:
            if pedido.status != 'paid':
                pedido.status='paid'
                pedido.save()
                pedido.delete_cart_paid()
        
            products_ids=[str(item.produto.id) for item in pedido.itens_pedido.all()]#type:ignore
        
            perfil=Perfil.objects.filter(usuario=pedido.usuario).first() if pedido.usuario else None
            telefone=perfil.telefone if perfil and hasattr(perfil,'telefone') else None
            valor_pedido=float(pedido.total_com_frete) if pedido and pedido.total_com_frete else 0.00
        
            obj=EnviaEvento()
            obj.enviar_evento_data(
                request=request,
                event_name='Purchase',
                event_id=str(pedido.pk),
                user_email=pedido.usuario.email if pedido.usuario else None,
                user_phone=telefone,
                custom_data={
                    'currency':'BRL',
                    'value':valor_pedido,
                    'order_id':str(pedido.pk),
                    'content_type':'product',
                    'content_ids':products_ids,
                    'num_items':pedido.itens_pedido.count()#type:ignore
                }
            )
        
        return render(request,'pagamentos/return.html',context)
        