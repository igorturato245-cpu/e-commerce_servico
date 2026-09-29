from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from carrinho.models import Carrinho
from utils.email_para_o_usuario import EmailForUser
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        agora=timezone.now()
        email_service=EmailForUser()
        
        uma_hora=agora - timedelta(hours=1)
        vinte_quatro_horas=agora - timedelta(hours=24)
        
        carrinhos_uma_hora=Carrinho.objects.filter(
            usuario__isnull=False,
            itens__isnull=False,
            email_pedido_abandonado_1=False,
            criado_em__lte=uma_hora,
            criado_em__gte=vinte_quatro_horas
        ).distinct()
        
        for carrinho in carrinhos_uma_hora:
            try:
                email_service.enviar_email_pedido_abandonado(carrinho,etapa=1)
                carrinho.email_pedido_abandonado_1=True
                carrinho.save(update_fields=['email_pedido_abandonado_1'])
                self.stdout.write(self.style.SUCCESS(f'E-mail enviado com sucesso para:{carrinho.usuario}'))
            except Exception as e:
                logger.error(f'Erro ao enviar e-mail, carrinho:{carrinho.pk},{e}')
                
        quarenta_oito_horas=agora - timedelta(hours=48)
        
        carrinhos_vinte_quatro_hora=Carrinho.objects.filter(
            usuario__isnull=False,
            itens__isnull=False,
            email_pedido_abandonado_1=True,
            email_pedido_abandonado_2=False,
            criado_em__lte=vinte_quatro_horas,
            criado_em__gte=quarenta_oito_horas
        ).distinct()
        
        for carrinho in carrinhos_vinte_quatro_hora:
            try:
                email_service.enviar_email_pedido_abandonado(carrinho,etapa=2)
                carrinho.email_pedido_abandonado_2=True
                carrinho.save(update_fields=['email_pedido_abandonado_2'])
                self.stdout.write(self.style.SUCCESS(f'E-mail enviado com sucesso para:{carrinho.usuario}'))
            except Exception as e:
                logger.error(f'Erro ao enviar e-mail, carrinho:{carrinho.pk},{e}')