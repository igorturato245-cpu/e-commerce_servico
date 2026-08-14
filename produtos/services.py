from .models import Product
from integrations.dropify.dropify_gateways import DropifyStrategy

class Produtos:
    def busca(self):
        
        obj=DropifyStrategy()
        
        lista_prod=obj.buscar_produtos()
        
        produto_base=Product.objects.first()
        id_categoria_padrao=produto_base.category_id if produto_base else 1
        
        for prod in lista_prod:
            Product.objects.update_or_create(
                erp_id=prod['erp_id'],
                defaults={
                    'name':prod['name'],
                    'preco':prod['preco'],
                    'preco_promocional':0,
                    'category_id':id_categoria_padrao,
                    'estoque':prod['estoque'],
                    'remote_stock':prod['estoque'],
                    'sku':prod['sku'],
                }
                )
            
        return True