from abc import ABC,abstractmethod


class IntegrationGatewayStrategy(ABC):
    
    @abstractmethod
    def buscar_produtos(self):
        pass
    
    @abstractmethod
    def enviar_pedido(self,pedido,endereco):
        pass
    
    @abstractmethod
    def checar_estoque(self,produto_erp_id):
        pass
    
    @abstractmethod
    def preco_atual_produto(self,produto_erp_id):
        pass
    
    @abstractmethod
    def status_pedido(self,pedido_id):
        pass