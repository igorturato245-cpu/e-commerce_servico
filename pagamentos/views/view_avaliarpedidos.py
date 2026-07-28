from django.shortcuts import render,redirect,get_object_or_404
from pagamentos.models import Pedido,Pedidoitem,Avaliation_product
from django.views import View
from django.contrib import messages


class AvaliarPedido(View):
    def get(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não esta logado.Faça seu loginpara acessar seus pedidos.')
            return redirect('cadastro_login:login')
        
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)
        
        ja_avaliou=Avaliation_product.objects.filter(pedido=pedido,usuario=request.user).exists()
        
        if ja_avaliou:
            messages.error(request,'Avaliação do pedido já existe.')
            return redirect('index:index')
        
        return render(request,'pagamentos/avaliar_produtos.html',{'pedido':pedido})
    
    def post(self,request,pedido_id):
        if not request.user.is_authenticated:
            messages.error(request,'Usuario não esta logado. Faça seu login para acessar seus pedidos.')
            return redirect('cadastro_login:login')
            
        pedido=get_object_or_404(Pedido,pk=pedido_id,usuario=request.user)
        
        ja_avaliou=Avaliation_product.objects.filter(pedido=pedido,usuario=request.user).exists()
        
        if ja_avaliou:
            messages.error(request,'Este pedido já foi avaliado.')
            return redirect('index:index')
           
        
        nota_site_str=request.POST.get('rating_site')
        nota_produto_str=request.POST.get('rating_prod')
        descricao=request.POST.get('feedback','')
        
        try:
            nota_site=int(nota_site_str) if nota_site_str else 5
            nota_produto=int(nota_produto_str) if nota_produto_str else 5
        except ValueError:
            messages.error(request,'Valores de avaliação inválidos.')
            return redirect('pagamentos:meus_pedidos')       
        
        itens_comprados=Pedidoitem.objects.filter(pedido=pedido)
        
        
        if not itens_comprados.exists():
            messages.error(request,'Carrinho vazio. Não é possível prosseguir com o carrinho vazio.')
            return redirect('carrinho:carrinho_url')
        
        for item in itens_comprados:
            
            Avaliation_product.objects.create(
                usuario=request.user,
                pedido=pedido,
                produto=item.produto,
                nota_site=int(nota_site) if nota_site else 5,
                nota_produto=int(nota_produto) if nota_produto else 5,
                comentario=descricao
            )
            
        messages.success(request,'Sucesso ao avaliar o produto.')
        return redirect('index:index')