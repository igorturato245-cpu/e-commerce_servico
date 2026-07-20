from django.db import models,transaction
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.db.models import Q
from utils.valida_cpf import valida_cpf
import re



class Perfil(models.Model):
    usuario=models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    idade=models.IntegerField()
    data_de_nascimento=models.DateField()
    telefone=models.CharField(max_length=15)
    cpf=models.CharField(max_length=14)
    
    def __str__(self) -> str:
        return f'{self.usuario}'
    
    def clean(self) -> None:
        error_messages={}
        
        cpf_enviado=self.cpf or None
        cpf_salvo=None
        perfil=Perfil.objects.filter(cpf=cpf_enviado).first()
        
        if perfil:
            cpf_salvo=perfil.cpf
            
            if cpf_enviado is not None and self.pk != perfil.pk:
                error_messages['cpf']='CPF já cadastrado'
                
        if not valida_cpf(self.cpf):
            error_messages['cpf']='Digite um cpf válido'
            
        
        tel_limpo=re.sub(r'\D','',str(self.telefone))
        
        if len(tel_limpo) < 10 or len(tel_limpo) > 11:
            error_messages['telefone']='O telefone deve ter o DDD +8 ou 9 dígitos (apenas números).'
            
        self.telefone=tel_limpo
        
        if error_messages:
            raise ValidationError(error_messages)
    
    class Meta:
        verbose_name='Perfil'
        verbose_name_plural='Perfis'
        
        

class Endereco_usuario(models.Model):
    usuario=models.ForeignKey(User,on_delete=models.CASCADE, related_name='enderecos')
    endereco=models.CharField(max_length=50)
    numero=models.CharField(max_length=5)
    complemento=models.CharField(max_length=30)
    bairro=models.CharField(max_length=30)
    cep=models.CharField(max_length=9)
    cidade=models.CharField(max_length=30)
    estado=models.CharField(max_length=2,default='SP',choices=(
        ('AC','Acre'),
        ('AL','Alagoas'),
        ('AP','Amapá'),
        ('AM','Amazonas'),
        ('BA','Bahia'),
        ('CE','Ceará'),
        ('DF','Distrito Federal'),
        ('ES','Espírito Santo'),
        ('GO','Goiás'),
        ('MA','Maranhão'),
        ('MT','Mato Grosso'),
        ('MS','Mato Grosso do Sul'),
        ('MG','Minas Gerais'),
        ('PA','Pará'),
        ('PB','Paraíba'),
        ('PR','Paraná'),
        ('PE','Pernambuco'),
        ('PI','Piauí'),
        ('RJ','Rio de Janeiro'),
        ('RN','Rio Grande do Norte'),
        ('RS','Rio Grande do Sul' ),
        ('RO','Rondônia'),
        ('RR','Roraima'),
        ('SC','Santa Catarina'),
        ('SP','São Paulo'),
        ('SE','Sergipe'),
        ('TO','Tocantins' ),
    ))
    padrao=models.BooleanField(default=False)
    
    
    def __str__(self) -> str:
        return f'{self.endereco}'
    
    
    def clean(self) -> None:
        erro_message={}
        
        cep_limpo=re.sub(r'\D','',str(self.cep))
        
        
        if not cep_limpo.isdigit and len(self.cep) != 8:
            erro_message['cep']='CEP inválido. Digite apenas números.'
            
        self.cep =  self.cep
        
        if erro_message:
            raise ValidationError(erro_message)


    def delete(self, *args, **kwargs):
        usuario=self.usuario
        era_padrao=self.padrao
        
        super().delete(*args, **kwargs)
        
        if era_padrao:
            novo=Endereco_usuario.objects.filter(usuario=usuario).order_by('-endereco').first()
            
            if novo:
                Endereco_usuario.objects.filter(pk=novo.pk).update(padrao=True)
                
                
    class Meta:
        verbose_name='Endereço'
        verbose_name_plural='Endereços'
        indexes = [models.Index(fields=['usuario', 'padrao']),]
        constraints=[
            models.UniqueConstraint(
                fields=['usuario'],
                condition=Q(padrao=True),
                name='unique_default_per_user'
            )
        ]
        
        
    def save(self,*args, **kwargs):
        with transaction.atomic():
            
            is_new=self.pk is None
            
            if self.padrao:
                Endereco_usuario.objects.filter(usuario=self.usuario,padrao=True
                                                ).exclude(pk=self.pk).update(padrao=False)
                
                super().save(*args, **kwargs)
                
            if is_new:
                Endereco_usuario.objects.filter(usuario=self.usuario,padrao=True
                                                ).exclude(pk=self.pk).update(padrao=False)
                
                self.padrao=True
                
        super().save(*args, **kwargs)
            