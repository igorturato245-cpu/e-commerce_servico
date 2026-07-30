from .models import Product
from integrations.dropify.dropify_gateways import DropifyStrategy

class Produtos:
    def busca(self):
        
        obj=DropifyStrategy()
        
        lista_prod=obj.buscar_produtos()
        
        for prod in lista_prod:
            Product.objects.update_or_create(
                erp_id=prod['erp_id'],
                defaults={
                    'name':prod['name'],
                    'preco':prod['preco'],
                    'estoque':prod['estoque'],
                    'remote_stock':prod['estoque']
                }
                )
            
        return True