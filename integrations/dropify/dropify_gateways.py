import json
import requests
from django.conf import settings
from integrations.dropify.dropify_adapter import DropifyAdapter
from integrations.dropify.base_integrations import IntegrationGatewayStrategy


class DropifyStrategy(IntegrationGatewayStrategy):
    def _get_config(self):
        client_id=getattr(settings,'DESTRIBUIDOR_CLIENT_ID',None)
        client_secret=getattr(settings,'DESTRIBUIDOR_CLIENT_SECRET',None)
        base_url=getattr(settings,'DESTRIBUIDOR_URL',None)
        
        if not client_id or not client_secret:
            raise RuntimeError('Credenciais (Client ID/Secret) da dropify não configuradas')
        
        auth_payload={
            'client_id':client_id,
            'client_secret':client_secret
        }
        
        auth_url=f'{base_url}/oauth'
        
        response=requests.post(auth_url,json=auth_payload,timeout=10)
        
        if response.status_code != 200:
            raise Exception(f'Falaha na autenticação Dropify:{response.text}')
        
        token=response.json().get('access_token')
        
        headers={
            'Content-Type':'application/json',
            'Authorization':f'Bearer {token}'
        }
        
        return base_url,headers
    
    
    def buscar_produtos(self):
        base_url,headers=self._get_config()
        
        skus_para_importar=[
            'DY14151',
            'DY14103-1',
            'DY14281',
            'DY14280-1',
            'DY14097',
            'DY23296',
            'DY23347',
            'DY14077',
            'DY14256',
            'DY14253',
            'DY5208',
            'DY10936'
        ]
        
        produtos_brutos=[]
        
        for sku in skus_para_importar:
            url=f'{base_url}/api/products/{sku}'
        
            response=requests.get(url,headers=headers,timeout=30)
        
            if response.status_code == 200:
                produtos_brutos.append(response.json())
                
        if not produtos_brutos:
            raise Exception('Nenhum produtos foi encontrado na Dropify')
           
        adaptador=DropifyAdapter()
        resposta_adapatador=adaptador.extrair_lista_produtos(produtos_brutos)
            
        return resposta_adapatador
        
    
    def enviar_pedido(self, pedido,endereco):
        base_url,headers=self._get_config()
        
        url=f'{base_url}/api/orders/create'
        
        adaptador=DropifyAdapter()
        payload=adaptador.montar_payload_pedido(pedido,endereco)
        
        
        response=requests.post(url,json=payload,headers=headers,timeout=30)
        
        if response.status_code in (200,201):
            return True
    
        else:
            raise Exception(f'Falha ao enviar pedido para o fornecedor:{response.text}')
        
    
    def checar_estoque(self, produto_erp_id):
        base_url,headers=self._get_config()
        
        url=f'{base_url}/products/{produto_erp_id}'
        
        response=requests.get(url,headers=headers,timeout=30)
        
        if response.status_code == 200:
            data=response.json()
            adaptador=DropifyAdapter()
            estoque_atual=adaptador.extrair_estoque(data)
            return estoque_atual
        
        return 0
    
    
    def preco_atual_produto(self, produto_erp_id):
        base_url,headers=self._get_config()
        
        url=f'{base_url}/products/{produto_erp_id}'
        
        response=requests.get(url,headers=headers,timeout=30)
        
        if response.status_code == 200:
            data=response.json()
            
            adaptador=DropifyAdapter()
            return adaptador.extrair_preco(data)
        
        return None
        
        
    def status_pedido(self, pedido_id):
        base_url,headers=self._get_config()
        
        url=f'{base_url}/orders/{pedido_id}'
        
        response=requests.get(url,headers=headers,timeout=30)
        
        if response.status_code == 200:
            data=response.json()
            adaptador=DropifyAdapter()
            return adaptador.traduzir_status_pedido(data)
        
        raise ValueError(f'Erro ao buscar status do pedido {pedido_id}')