from django.shortcuts import render,redirect
from carrinho.models import Carrinho
from django.views import View
from produtos.models import Product
from pagamentos.models import Cupons

class _get_card_for_request:
    def get_carrinho(self,request):
        if request.user.is_authenticated:
            card,_=Carrinho.objects.get_or_create(usuario=request.user)
            return card
        
        session_key=request.session.session_key
        if not session_key:
            request.session['carrinho_ativo']=True
            request.session.save()        
            session_key=request.session.session_key
            
            
        card,_=Carrinho.objects.get_or_create(session_key=session_key)
            
        return card
        
        
        
class carrinho(_get_card_for_request,View):
    
    def get(self,request,*args, **kwargs):
                
                
        carrinho=self.get_carrinho(request)
                
                
        if not carrinho:
            itens=[]
            subtotal=0
                    
        else:
                   
            itens=carrinho.itens.select_related('produto').all()#type:ignore
                    
            subtotal=carrinho.total()
                    
            if carrinho.cupom:
                if carrinho.cupom.esta_valido():
                    subtotal=carrinho.total()
            
        produtos_exibicao=Product.objects.filter(preco__lte=100)
        
        contexto={
            'items':itens,
            'total':subtotal,
            'produtos':produtos_exibicao
        }
                
        return render(request,'carrinho/carrinho.html', contexto)
            
            
    
    def post(self,request,*args, **kwargs):            
        carrinho=self.get_carrinho(request)                
                
        cupom=request.POST.get('cupom')
                
        cupom_uso=Cupons.objects.filter(codigo__iexact=cupom).first()
    
        if cupom_uso:
            if cupom_uso.esta_valido():
                carrinho.cupom=cupom_uso#type:ignore
        
        carrinho.save(update_fields=['cupom'])     
                    
        return redirect('carrinho:carrinho_url')