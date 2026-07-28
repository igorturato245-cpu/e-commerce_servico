from abc import ABC,abstractmethod
          
        
class PaymentGatewayStrategy(ABC):
        
    @abstractmethod
    def gerar_pagamento(self,pedido,endereco,return_url,notification_url):
        pass
    
    @abstractmethod
    def pega_notificacao(self,notification_id):
        pass
    
    @abstractmethod
    def valida_notificacao(self,data):
        pass
    
    @abstractmethod
    def reembolso_transacao(self,charge_id,amount=None):
        pass