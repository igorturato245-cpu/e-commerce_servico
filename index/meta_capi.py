import hashlib
import time
import requests
from django.conf import settings
from abc import ABC,abstractmethod


class ConverteHash:
    def hash_data(self,value):
        
        if not value:
            return None
        
        clean_val=value.strip().lower()
        
        return hashlib.sha256(clean_val.encode('utf-8')).hexdigest()
    
class EnviaEvento:
    def enviar_evento_data(self,request, event_name, event_id=None, custom_data=None, user_email=None, user_phone=None):
        
        url=f"https://graph.facebook.com/{settings.META_API_VERSION}/{settings.META_PIXEL_ID}/events"
        
        cliente_id_address=request.META.get('HTTP_X_FORWARDED_FOR',request.META.get('REMOTE_ADDR'))
        
        if cliente_id_address and ',' in cliente_id_address:
            cliente_id_address=cliente_id_address.split(',')[0].strip()
            
        cliente_user_agent=request.META.get('HTTP_USER_AGENT','')
        
        obj_hash=ConverteHash()
        
        obj=Building()
        user_data=obj.cria_dados_usuarios(cliente_id_address,cliente_user_agent)
        
        if user_email:
            user_data["em"]=[obj_hash.hash_data(user_email)]
        if user_phone:
            user_data["ph"]=[obj_hash.hash_data(user_phone)]
            
        event_payload=obj.cria_payload(request,event_name,user_data)
        
        if event_id:
            event_payload['event_id']=str(event_id)
            
        if custom_data:
            event_payload['custom_data']=custom_data
            
        payload_response=obj.cria_payload_response(event_payload)
        
        try:
            response=requests.post(url,json=payload_response,timeout=5)
            return response.json()
        
        except Exception as e:
            print(f"[Meta CAPI error]:{e}")
            return None
            
        

class AbstractBuilding(ABC):
    @abstractmethod
    def cria_dados_usuarios(self,cliente_ip, cliente_user):
        pass
    
    @abstractmethod
    def cria_payload(self,request,event_name,user_data):
        pass
    
    @abstractmethod
    def cria_payload_response(self,event_payload):
        pass
        
        
        
class Building(AbstractBuilding):
    def cria_dados_usuarios(self,cliente_ip, cliente_user):
        
        user_data={
            'client_ip_address':cliente_ip,
            'client_user_agent':cliente_user
        }
        
        return user_data
    
    def cria_payload(self,request,event_name,user_data):
        event_payload={
            'event_name':event_name,
            'event_time':int(time.time()),
            'action_source':'website',
            'event_source_url':request.build_absolute_uri(),
            'user_data':user_data
        }
        
        return event_payload
    
    def cria_payload_response(self,event_payload):
        if 'custom_data' in event_payload and 'value' in event_payload['custom_data']:
            try:
                val=float(event_payload['custom_data']['value'])
                event_payload['custom_data']['value']=round(val,2)
            except (ValueError,TypeError):
                event_payload['custom_data']['value']=0.00
                
        payload={
            'data':[event_payload],
            'access_token':settings.META_ACCESS_TOKEN
        }
        
        return payload
    
    