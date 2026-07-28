import re
from abc import ABC, abstractmethod


class apenas_numeros_abstract(ABC):
    @abstractmethod
    def apenas_numeros(self,valor):
        pass
    
    
class apenas_numeros_concreto(apenas_numeros_abstract):
    def apenas_numeros(self,valor):
        if not valor:
            return ""
        return re.sub(r'\D','',str(valor))