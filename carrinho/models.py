from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models import F,Sum,DecimalField,ExpressionWrapper
from produtos.models import Product



class Carrinho(models.Model):
    usuario=models.ForeignKey(User, blank=True, null=True, db_index=True, on_delete=models.CASCADE)
    session_key=models.CharField(max_length=50,blank=True,null=True,db_index=True, unique=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    atualizado_em=models.DateTimeField(auto_now=True)
    email_pedido_abandonado_1=models.BooleanField(default=False)
    email_pedido_abandonado_2=models.BooleanField(default=False)
    
    
    def total(self):
        total_produtos=self.itens.aggregate(#type:ignore
            soma_total=Sum(
                ExpressionWrapper(
                    F('quantidade') * F('preco_unitario'),
                    output_field=DecimalField()
                )
            )
        )
        
        total=total_produtos['soma_total']
        
        return total or Decimal('0.00')
    
    def __str__(self) -> str:
        if self.usuario:
            return f'Carrinho de {self.usuario.username} - criado em {self.criado_em}'
        if self.session_key:
            return f'Carrinho session {self.session_key} - criado em {self.criado_em}'
        return f'Carrinho criado em {self.criado_em.strftime('%d/%m/%Y às %H:%M:%S')}'
    
    
class Item_carrinho(models.Model):
    carrinho=models.ForeignKey(Carrinho,related_name='itens',on_delete=models.CASCADE)
    produto=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantidade=models.PositiveIntegerField(default=1)
    preco_unitario=models.DecimalField(max_digits=10,decimal_places=2,null=True)
    
    
    def atualiza_qtd(self,qtd):
        quantidade=max(1,qtd)
        
        limite_real=min(10,self.produto.estoque)
        
        if quantidade > limite_real:
            self.quantidade=limite_real
            
        else:
            self.quantidade=quantidade
            
        return self.quantidade
    
    def save(self,*args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario=self.produto.get_preco()
            
        super().save(*args, **kwargs)
            
    def __str__(self) -> str:
        return f'{self.produto.name}-{self.quantidade}'
