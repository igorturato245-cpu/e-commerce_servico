from abc import ABC,abstractmethod

class PayloadAdapter(ABC):
    @abstractmethod
    def make_payload(self,pedido,endereco,return_url,notification_url,cpf_cliente,cep_cliente,items):
        pass
    
    @abstractmethod
    def parse_notification(self,data,notification_id):
        pass
    
    
class PagSeguroCreatePayload(PayloadAdapter):
    def make_payload(self, pedido, endereco, return_url, notification_url, cpf_cliente, cep_cliente):
        
        items=[]
        
        for item in pedido.items.all():
            items.append({
                'reference_id':item.produto_id_string or str(item.id),
                'name':item.produto_name[:100],
                'quanntity':item.quantidade,
                'unit_amount':int(round(item.price * 100))
            })
        
        payload={
            'reference_id':f'PED-{pedido.id}',
            'customer':{
                'name':pedido.usuario.get_full_name() or pedido.usuario.username,
                'email':pedido.usuario.email,
                'tax_id':cpf_cliente,
            },
            'items':items,
            'shipping':{
                'type':'FIXED',
                'amount':int(round(pedido.valor_frete * 100)),
                'address':{
                    'street':endereco.endereco,
                    'number':str(endereco.numero),
                    'complement':endereco.complemento or "",
                    'locality':endereco.bairro,
                    'city':endereco.cidade,
                    'region_code':endereco.estado,
                    'country':'BRA',
                    'postal_code':cep_cliente
                }
            },
            'notification_urls':[notification_url],
            'payment_notification_urls':[notification_url],
            'redirect_url':return_url,
            'payment_methods':[
                {'type':'CREDIT_CARD'},
                {'type':'BOLETO'},
                {'type':'PIX'},
            ],
        }
        
        return payload
    
    
    def parse_notification(self, data, notification_id):
        
        charge={}
        
        if notification_id.starstwith('CHAR_'):
            charge=data
            ref=data.get('reference_id')
        elif notification_id.starstwith('CHCK_'):
            ref=data.get('reference_id')
            orders=data.get('orders',[{}])
            order=orders[0] if orders else {}
            charges=order.get('charges',[{}])
            charge=charges[0] if charges else {}
        else:
            ref=data.get('reference_id')
            charges=data.get('charges',[{}])
            charge=charges[0] if charges else {}
            
        status=charge.get('status','WAITING')
        
        return {
            'reference':ref,
            'status':status,
            'code':notification_id,
            'charge_id':charge.get('id'),
            'lastEventDate':charge.get('paid_at') or data.get('created_at'),
            'grossAmount':charge.get('amount',{}).get('value',0) / 100
        }