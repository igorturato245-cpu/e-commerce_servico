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
    
    def sincroniza_estoque(self):
        
        strategy=DropifyStrategy()
        produtos=Product.objects.exclude(erp_id__isnull=True).exclude(erp_id='')
        
        for produto in produtos:
            try:
                novo_estoque=strategy.checar_estoque(produto.erp_id)
                produto.estoque=novo_estoque
                produto.remote_stock=novo_estoque
                produto.save(update_fields=['estoque','remote_stock'])
                
                print(f'SKU:{produto.sku} | Estoque:{novo_estoque} | Nome:{produto.name}')
                
            except Exception as e:
                print(f'❌ SKU:{produto.erp_id} | Falha ao atualizar:{str(e)}')
                continue
            
        return True