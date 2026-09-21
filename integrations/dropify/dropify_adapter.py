from abc import ABC, abstractmethod
from decimal import Decimal
from produtos.models import Product

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
    
    @abstractmethod
    def montar_payload_frete(self,cep,itens):
        pass
    
    @abstractmethod
    def traduzir_frete(self,data):
        pass
    
    
class DropifyAdapter(IntegrationAdapterAbstract):
    
    def extrair_lista_produtos(self, data):
        
        retorno=[]
        
        if isinstance(data,list):
            lista_suja=data
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
    
    def montar_payload_frete(self, cep, itens):
        from produtos.models import Product

        cep_limpo = "".join(filter(str.isdigit, str(cep)))
        itens_payload = []

        for item in itens:
            produto = None
            quantidade = 1
            preco = 0
            sku = ''

            # CENÁRIO A: Veio como dicionário (ex: {'id': 'DY14142', 'quantity': 1})
            if isinstance(item, dict):
                item_id = str(item.get('id') or item.get('produto_id') or '').strip()
                quantidade = item.get('quantity') or item.get('quantidade', 1)

                if item_id:
                    # Se for apenas números (ex: '2'), busca pela chave primária (pk)
                    if item_id.isdigit():
                        produto = Product.objects.filter(pk=int(item_id)).first()
                    # Se tiver letras (ex: 'DY14142'), busca pelo SKU ou erp_id
                    else:
                        produto = (
                            Product.objects.filter(sku=item_id).first() 
                            or Product.objects.filter(erp_id=item_id).first()
                        )
                        sku = item_id  # O próprio item_id já é o SKU!

                if produto:
                    sku = produto.sku or produto.erp_id or sku
                    preco = produto.get_preco() if hasattr(produto, 'get_preco') else produto.preco
                else:
                    sku = sku or item.get('sku', '')
                    preco = item.get('price', item.get('preco', 0))

            # CENÁRIO B: Veio como objeto (Item_carrinho ou Pedidoitem)
            else:
                produto = getattr(item, 'produto', None)
                quantidade = getattr(item, 'quantidade', 1)

                if produto:
                    sku = produto.sku or produto.erp_id or ''
                    preco = getattr(item, 'preco_unitario', None)
                    if preco is None:
                        preco = produto.get_preco() if hasattr(produto, 'get_preco') else produto.preco
                else:
                    sku = getattr(item, 'produto_id_str', '')
                    preco = getattr(item, 'price', 0)

            preco_em_centavos = str(int(round(float(preco or 0) * 100)))

            if produto:
                itens_payload.append({
                    "sku": str(sku),
                    "price": preco_em_centavos,
                    "quantity": int(quantidade),
                    "height": produto.heigth,
                    "length": produto.length,
                    "width": produto.width,
                    "weight": produto.weigth,
                    })

        payload_final = {
            "zipcode": cep_limpo,
            "items": itens_payload
        }

        print(f"[DEBUG PAYLOAD PRONTO PARA DROPIFY]: {payload_final}")
        return payload_final
        
    def traduzir_frete(self, data):
        
        if not data.get('success'):
            return None
        
        metodos=data.get('shippingMethods',[])
        if not metodos:
            return None
        
        opcoes=[]
        
        for m in metodos:
            opcoes.append({
                'id': m.get('shippingMethodId'),
                'name': m.get('shippingMethodName'),
                'price': Decimal(m.get('shippingCost', 0)) / Decimal(100),  # 3395 vira Decimal('33.95')
                'delivery_days': m.get('deliveryTime', 0)
            })
            
        melhor_opcao=min(opcoes,key=lambda x:x['price'])
        
        
        return {'melhor_opcao':melhor_opcao}