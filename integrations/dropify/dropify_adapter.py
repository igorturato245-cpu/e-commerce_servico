from abc import ABC, abstractmethod

class IntegrationAdapterAbstract(ABC):
    
    @abstractmethod
    def extrair_lista_produtos(self,data):
        pass    
    
    @abstractmethod
    def montar_payload_pedido(self,pedido,endereco):
        pass
    
    @abstractmethod
    def extrair_estoque(self,data):
        pass
    
    @abstractmethod
    def extrair_preco(self,data):
        pass
    
    @abstractmethod
    def traduzir_status_pedido(self,data):
        pass
    
    
class DropifyAdapter(IntegrationAdapterAbstract):
    
    def extrair_lista_produtos(self, data):
        
        retorno=[]
        
        if isinstance(data,list):
            lista_suja=[]
        elif "_embedded" in data and "products" in data["_embedded"]:
            lista_suja=data["_embedded"]["products"]
        else:
            lista_suja=data.get('data',[])
        
        for infos in lista_suja:
            sku_produto=infos.get('sku','')
            retorno.append({
                'erp_id':sku_produto,
                'name':infos.get('name',''),
                'preco':infos.get('suggestedRetailPrice',0)/100,
                'estoque':infos.get('stockQuantity',0),
                'sku':sku_produto
            })
            
        return retorno
    
    def montar_payload_pedido(self, pedido,endereco):
        
        perfil=pedido.usuario.perfil if hasattr(pedido.usuario,'perfil') else None
        
        cpf_cliente=perfil.cpf if perfil else ''
        telefone_cliente=perfil.telefone if perfil else ''
        
        items=[]
        
        for item in pedido.itens_pedido.all():
            items.append({
                'product':item.produto_name,
                'sku':item.produto.sku if item.produto and item.produto.sku else str(item.produto_id_str),
                'quantity':item.quantidade,
                'price':{
                    'unit_amount':str(int(round(item.price * 100))),
                    'currency':'BRL'
                }
            })
        
        payload={
                "externalOrderId": str(pedido.id),
                "salesChannel": "Luvia Home",
                "consumer": {
                    "cpf": cpf_cliente,
                    "name":pedido.usuario.get_full_name() or pedido.usuario.first_name,
                    "email": pedido.usuario.email,
                    "phone":telefone_cliente,
                    "mobilePhone": telefone_cliente,
                    "address": {
                        "country": "Brasil",
                        "state": endereco.estado,
                        "postalCode": endereco.cep,
                        "city": endereco.cidade,
                        "district": endereco.bairro,
                        "street": endereco.endereco,
                        "number": str(endereco.numero),
                        "complement":endereco.complemento or ""
                        }
                    },
                "items": items,
                "shippingMethod": "CUSTOM_LABEL"
                }
        
        
        return payload
    
    
    def extrair_estoque(self, data):
        estoque=data.get('stockQuantity', 0)          
        
        return estoque
    
    
    def extrair_preco(self, data):
        
        preco=data.get('suggestedRetailPrice', 0)
        return preco / 100
    
    
    def traduzir_status_pedido(self, data):
        
        status=data.get('status', 'PENDING')
        
        return status