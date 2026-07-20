from django.db import models

class Contato(models.Model):
    nome = models.CharField('Nome', max_length=40)    
    emall = models.EmailField('E-mail')
    texto=models.TextField('Mensagem', max_length=400)
    
    class Meta:
        verbose_name = "Contato"
        