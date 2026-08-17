"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('index.urls', namespace='index')),
    path('produtos/', include('produtos.urls', namespace='produtos')),
    path('cadastro/', include('cadastro_de_usuarios.urls', namespace='cadastro_login')),
    path('carrinho/',include('carrinho.urls',namespace='carrinho')),
    path('pagamentos/',include('pagamentos.urls',namespace='pagamentos')),
    path('senha/reset/',auth_view.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
    ),name='password_reset'),
    path('senha/reset/enviado',auth_view.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('senha/reset/<uidb64>/<token>/',auth_view.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('senha/reset/completo/',auth_view.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
]
