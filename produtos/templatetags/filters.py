from django.template import Library
from utils.formata_preco import oficial_formatar_preco


register=Library()
merge=oficial_formatar_preco()

@register.filter
def formata_preco(preco):
    return merge.formata_preco(preco)