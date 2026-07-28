from django.urls import path
from views.view_checkout import Checkout
from views.view_avaliarpedidos import AvaliarPedido
from views.view_retorno_pagamento import RetornoPagamento
from views.view_meuspedidos import MeusPedidos,DetalhePedido
from views.view_reembolso import Solicitacao_reembolso,AnaliseReembolso
from views.view_cancelamentopedido import CancelarPedido,ConclusaCancelamento
from views.view_fachada import StartPaymentView,RetryPaymentView,CancelledRefundedView,PagseguroNotificationView,RefundedSolicitationAprovedView


app_name='pagamentos'

urlpatterns = [
    path('checkout/',Checkout.as_view(),name='checkout'),
    path('start/',StartPaymentView.as_view(),name='start_payment'),
    path('retry/<int:pedido_id>/',RetryPaymentView.as_view(),name='retry_payment'),
    path('cancel/<int:pedido_id>/',CancelledRefundedView.as_view(),name='cancel_refunded_payment'),
    path('return/payment/',RetornoPagamento.as_view(),name='payment_return'),
    path('notification/',PagseguroNotificationView.as_view(),name='pagseguro_notify'),
    path('meus-pedidos/',MeusPedidos.as_view(),name='meus_pedidos'),
    path('pedido/<int:pedido_id>/',DetalhePedido.as_view(),name='detalhe_pedido'),
    path('avaliar-pedido/<int:pedido_id>/',AvaliarPedido.as_view(),name='avaliar_pedido'),
    path('cancelar-pedido/<int:pedido_id>/',CancelarPedido.as_view(), name='devolucao_reembolso_direto'),
    path('solicitacao-reembolso-pedido/<int:pedido_id>/',Solicitacao_reembolso.as_view(),name='solicitacao_reembolso'),
    path('analise-reembolso-pedido/<int:pedido_id>',AnaliseReembolso.as_view(),name='analise_reembolso'),
    path('solicitacao-reembolso-pedido/<int:pedido_id>/',RefundedSolicitationAprovedView.as_view(),name='solicitacao_reembolso_aprovada'),
    path('conclucsao-cancelamento-automatico/<int:pedido_id>/',ConclusaCancelamento.as_view(),name='conclusao_cancelamento_automatico')
]
