from django.shortcuts import render
from carrinho.models import Carrinho
from django.views import View


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
    

        contexto={
            'items':itens,
            'total':subtotal
        }
        
        return render(request,'carrinho/carrinho.html', contexto)
        
        
        
            