from carrinho.models import Carrinho,Item_carrinho
from abc import ABC, abstractmethod

class carts_merg(ABC):
    @abstractmethod
    def marge_cards(self,old_session_key,user):
        pass
    
    
class oficial_merg(carts_merg):
    def marge_cards(self, old_session_key, user):
        
        card_anon=Carrinho.objects.filter(session_key=old_session_key).first()
        card_user,_=Carrinho.objects.get_or_create(usuario=user)
        
        if not card_anon:
            return
        
        for itens in card_anon.itens.all():#type:ignore
            user_new_card,create=Item_carrinho.objects.get_or_create(
                carrinho=card_user,
                produto=itens.produto,
                defaults={'quantidade':itens.quantidade}
            )
            
            if not create:
                new_qtd=user_new_card.quantidade + itens.quantidade
                user_new_card.atualiza_qtd(new_qtd)
                user_new_card.save()
                
        card_anon.delete()