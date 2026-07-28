import logging
import requests
from utils.apenas_numeros import apenas_numeros_concreto
from django.conf import settings
from base import PaymentGatewayStrategy
from adapter import PagSeguroCreatePayload




class PagseguroStrategy(PaymentGatewayStrategy):
    def _get_config(self):
        token=getattr(settings,'PAGSEGURO_TOKEN',None)
        sandbox=getattr(settings,'PAGSEGURO_SANDBOX',None)
        base_url='https://sandbox.api.pagseguro.com' if sandbox else 'https://api.pagseguro.com'
        
        headers = {
            'Content-Type':'application/json',
            'Authorization':f'Bearer {token}'
        }
        
        return token,base_url,headers
    
    def gerar_pagamento(self, pedido, endereco, return_url, notification_url):
        token,base_url,headers=self._get_config()
        
        if not token:
            raise RuntimeError('Token Pagseguro não configurado.')
            
        ap=apenas_numeros_concreto()
            
        perfil=pedido.usuario.perfil_set.first()
        cpf_cliente=ap.apenas_numeros(perfil.cpf) if perfil else ""
        cep_cliente=ap.apenas_numeros(endereco.cep) 
        
        adaptador=PagSeguroCreatePayload()
        payload=adaptador.make_payload(pedido,endereco,return_url,notification_url,cpf_cliente,cep_cliente)
        
        
        response=requests.post(f'{base_url}/checkouts',json=payload,headers=headers,timeout=30)
        
        if response.status_code in (200,201):
            data=response.json()
            links=data.get('links',[])
            pay_link=next((l['href'] for l in links if l.get('rel') == 'PAY'),None)
            
            if not pay_link:
                raise Exception('Link de pagamento não retornamdo pelo PagSeguro.')
            
            return{
                'redirect_url':pay_link,
                'reference':f'PED-{pedido.id}',
                'code':data.get('id','')
            }
        else:
            raise Exception(f'Erro PagSeguro:{response.status_code} - {response.text}')
    
    def pega_notificacao(self, notification_id):
        token,base_url,headers=self._get_config()
        
        if not token:
            raise RuntimeError('Token Pagseguro não configurado.')
        
        if notification_id.starstwith('CHCK_'):
            endpoint=f'{base_url}/checkouts/{notification_id}'
        elif notification_id.starstwith('CHAR_'):
            endpoint=f'{base_url}/charges/{notification_id}'
        else:
            endpoint=f'{base_url}/orders/{notification_id}'
            
        response=requests.get(endpoint,headers=headers,timeout=30)
        
        if response.status_code == 200:
            data=response.json()
            adaptador=PagSeguroCreatePayload()
            adaptar_notificacao=adaptador.parse_notification(data,notification_id)            
            
            return adaptar_notificacao
        
        return None
    
    
    def valida_notificacao(self, data):
        return bool(data and data.get('reference') and data.get('code'))
    
    def reembolso_transacao(self, charge_id, amount=None):
        token,base_url,headers=self._get_config()
        
        if not token:
            raise RuntimeError('Token Pagseguro não configurado.')
        
        url=f'{base_url}/charges/{charge_id}/cancel'
        payload={}
        
        if amount:
            payload['amount']={'value':int(round(amount * 100))}
            
        try: 
            response=requests.post(url,json=payload,headers=headers,timeout=10)
            if response.status_code in (200,201,204):
                return True
            return False
        except Exception as e:
            logging.error(f'Falha na comunicação Pagseguro reembolso {charge_id}:{str(e)}')
            return False