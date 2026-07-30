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
        
        lista_suja=data.get('data',[])
        
        for infos in lista_suja:
            retorno.append({
                'erp_id':infos.get('id'),
                'name':infos.get('title'),
                'preco':infos.get('suggestedRetailPrice',0)/100,
                'estoque':infos.get('stockQuantity',0)
            })
            
        return retorno
    
    def montar_payload_pedido(self, pedido,endereco):
        
        items=[]
        
        for item in pedido.items.all():
            items.append({
                'reference_id':item.produto_id_string or str(item.id),
                'name':item.produto_name,
                'quantity':item.quantidade,
                'unit_amount':int(round(item.price * 100))
            })
            
        perfil=pedido.usuario.perfil_set.first()
        
        payload={
                "externalOrderId": str(pedido.id),
                "salesChannel": "Luvia Home",
                "consumer": {
                    "consumerType": "naturalPerson",
                    "name":pedido.usuario.get_full_name() or pedido.usuario.first_name,
                    "email": pedido.usuario.email,
                    "phoneNumber": perfil.telefone if perfil else "",
                    "mobilePhoneNumber": perfil.telefone if perfil else "",
                    "cpfCnpj": perfil.cpf if perfil else "",
                    "address": {
                        "postalCode": endereco.cep,
                        "street": endereco.endereco,
                        "number": str(endereco.numero),
                        "district": endereco.bairro,
                        "city": endereco.cidade,
                        "state": endereco.estado,
                        "country": "Brasil"
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