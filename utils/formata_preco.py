from abc import ABC,abstractmethod


class abstract_formatar_preco(ABC):
    @abstractmethod
    def formata_preco(self,preco):
        pass
    
    
class oficial_formatar_preco(abstract_formatar_preco):
    def formata_preco(self,preco):
        return f'R$ {preco:.2f}'.replace('.',',')