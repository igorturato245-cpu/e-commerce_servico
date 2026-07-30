from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



class EmailForUser:
    def enviar_email_pedido_recebido(self,pedido):
        subject=f'Pedido recebido #{pedido.id}'
        from_email=settings.DEFAULT_FROM_EMAIL
        to=[pedido.usuario.email]
        
        html_content=render_to_string('emails/email_pedido_recebido.html',{'pedido':pedido})
        text_content=strip_tags(html_content)
        
        email=EmailMultiAlternatives(subject,text_content,from_email,to)
        email.attach_alternative(html_content,'text/html')
        email.send()
        
        
    def enviar_email_status_pedido(self,pedido):
        subject=f'Atualização no seu pedido #{pedido.id}'
        from_email=settings.DEFAULT_FROM_EMAIL
        to=[pedido.usuario.email]
            
        html_content=render_to_string('emails/email_pedido.html',{'pedido':pedido})
        text_content=strip_tags(html_content)
            
        email=EmailMultiAlternatives(subject,text_content,from_email,to)
        email.attach_alternative(html_content,'text/html')
        email.send()
            
    def enviar_email_status_erp_pedido(self,pedido):
        subject=f'Atualização no seu pedido #{pedido.id}'
        from_email=settings.DEFAULT_FROM_EMAIL
        to=[pedido.usuario.email]
                
        html_content=render_to_string('emails/email_pedido_erp.html',{'pedido':pedido})
        text_content=strip_tags(html_content)
                
        email=EmailMultiAlternatives(subject,text_content,from_email,to)
        email.attach_alternative(html_content,'text/html')
        email.send()
        
    def enviar_email_status_reembolso(self,solicitacao,pedido):
        subject=f'Atualização do seu reembolso - Pedido #{pedido.id}'
        from_email=settings.DEFAULT_FROM_EMAIL
        to=[pedido.usuario.email]
            
        contexto={
            'solicitacao':solicitacao,
            'pedido':pedido
        }
                    
        html_content=render_to_string('emails/email_cancelamento_status.html',contexto)
        text_content=strip_tags(html_content)
                    
        email=EmailMultiAlternatives(subject,text_content,from_email,to)
        email.attach_alternative(html_content,'text/html')
        email.send()
        
        
    def enviar_email_cancelamento_direto(self,pedido):
            subject=f'Confirmação de cancelamento - Pedido #{pedido.id}'
            from_email=settings.DEFAULT_FROM_EMAIL
            to=[pedido.usuario.email]
                    
            html_content=render_to_string('emails/email_cancelamento_direto.html',{'pedido':pedido})
            text_content=strip_tags(html_content)
                    
            email=EmailMultiAlternatives(subject,text_content,from_email,to)
            email.attach_alternative(html_content,'text/html')
            email.send()