from django.db import models

class Contato(models.Model):
    nome = models.CharField('Nome', max_length=40)    
    email = models.EmailField('E-mail')
    texto=models.TextField('Mensagem', max_length=400)
    
    class Meta:
        verbose_name = "Contato"
        verbose_name_plural="Contatos"
        
        def __str__(self) -> str:
            return f"Mensagem de {self}"
        