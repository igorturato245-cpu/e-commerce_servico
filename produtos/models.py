from django.db import models
from decimal import Decimal
from django.utils.text import slugify
from django.db.models.expressions import Combinable
from django.contrib.auth.models import User
from django.db.models import Avg


class Category(models.Model):
    name=models.CharField('Name', max_length=200,unique=True)
    slug=models.CharField('Slug', max_length=200,unique=True)
    
    
    class Meta:
        verbose_name='Categoria'
        verbose_name_plural='Categorias'
        ordering=['name']
        
    def __str__(self) -> str:
        return self.name
    
    
class Product(models.Model):
    category=models.ForeignKey(Category,related_name='categoria_produto',on_delete=models.CASCADE)
    name=models.CharField('Name',max_length=200)
    slug=models.SlugField('Slug',max_length=200,unique=True)
    descrixcao=models.TextField('Descrição',blank=True)
    preco=models.DecimalField('Preço', max_digits=10,decimal_places=2)
    preco_promocional=models.DecimalField('Preço promocional',max_digits=10,decimal_places=2)
    estoque=models.PositiveIntegerField('Estoque', default=0)
    disponivel=models.BooleanField('Disponível',default=True)
    ofertas_do_dia=models.BooleanField('Ofertas do dia',default=False)
    imagem=models.ImageField('Imagem',upload_to='produtos/%Y/%m/%d',blank=True,null=True)
    imagem_url=models.URLField('Imagem remota', blank=True,null=True)
    criado=models.DateTimeField('Criado em',auto_now_add=True)
    atulizado=models.DateField('Atualizado em', auto_now=True)
    sku=models.CharField('Sku',max_length=100, blank=True,null=True)
    erp_id=models.CharField('erp_id', max_length=128,blank=True,null=True)
    remote_price=models.DecimalField('Preço remoto', max_digits=10,decimal_places=2,null=True,blank=True)
    remote_stock=models.IntegerField('Preço remoto', null=True,blank=True)
    last_synced=models.DateTimeField('Última sincronização',auto_now=True,blank=True,null=True)
    
    class Meta:
        verbose_name='Produto'
        verbose_name_plural='Produtos'
        ordering=['criado']
        indexes=[models.Index(fields=['category','disponivel']),models.Index(fields=['ofertas_do_dia','disponivel'])]
        
        
    def __str__(self) -> str:
        return self.name
    
    def get_preco(self):
        if self.preco_promocional and self.preco_promocional > Decimal('0.00'):
            return self.preco_promocional
        return self.preco
    
    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            
        if not isinstance(self.estoque,Combinable ):
            self.disponivel = self.estoque > 2
            
        super().save(*args, **kwargs)
        

class ProdutoImagem(models.Model):
    produto=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='Carrossel')
    foto=models.ImageField('Imagens',upload_to='produtos/%Y/%m/%d',blank=True,null=True)
    
    def __str__(self) -> str:
        return f'Carrossel de fotos do produto {self.produto.name}'
    
    
class Avaliation_product(models.Model):
    usuario=models.ForeignKey(User,on_delete=models.CASCADE)
    #pedido=models.ForeignKey('pagamentos.Pedido',on_delete=models.CASCADE)
    produto=models.ForeignKey(Product,on_delete=models.CASCADE)
    
    nota_site=models.IntegerField(default=5)
    nota_produto=models.IntegerField(default=5)
    comentario=models.TextField(max_length=400,blank=True,null=True)
    
    def __str__(self) -> str:
        return f'Avaliação de {self.usuario.username} para o produto:{self.produto.name}'
    
    
    @property
    def media_avaliacoes(self):
        media = Avaliation_product.objects.filter(produto=self.produto).aggregate(avg=Avg('nota_produto'))['avg']

        return round(media, 1) if media is not None else 0.0 
    
    @property
    def estrelas_cheias(self):
        return range(int(self.media_avaliacoes))
    
    @property
    def tem_meia(self):
        return (self.media_avaliacoes - int(self.media_avaliacoes)) >= 0.5
    
    @property
    def estrelas_vazias(self): 
        vazia=5-int(self.media_avaliacoes)
        
        if self.tem_meia:
            vazia -= 1
        
        return range(vazia)
    
    
class Token_Fonecedor(models.Model):
    access_token=models.TextField()
    refresh_token=models.TextField()
    update_at=models.DateTimeField(auto_now=True)  