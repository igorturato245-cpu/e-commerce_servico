from typing import Any

from django.core.management.base import BaseCommand
from carrinho.tasks import ConcretLimpezaCarrinho

class Command(BaseCommand):
    help='Remove carrinhos abandonados há mais de 7 dias.'
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write('Iniciando limpeza manual...')
        obj=ConcretLimpezaCarrinho()
        resultado=obj.executa_limpeza_carrinho()
        self.stdout.write(self.style.SUCCESS(resultado))