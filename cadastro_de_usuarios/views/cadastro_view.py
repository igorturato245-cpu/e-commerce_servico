from typing import Any

from django.shortcuts import render,redirect
from django.views import View
from cadastro_de_usuarios.forms import PerfilForm,Cadastroform
from django.http import HttpRequest
from cadastro_de_usuarios.models import Perfil
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.shortcuts import get_object_or_404
from carrinho.services import oficial_merg



class BaseCadastro(View):
    template_name='cadastro_de_usuarios/cadastro.html'
    
    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        
        self.perfil=None
        
        if self.request.user.is_authenticated:
            self.perfil=Perfil.objects.filter(
                usuario=self.request.user
            ).first()
            
            self.contexto={
                'form_cadastro':Cadastroform(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user
                ),
                'perfil_cadastro':PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.contexto={
                'form_cadastro':Cadastroform(
                    data=self.request.POST or None    
                ),
                'perfil_cadastro':PerfilForm(
                    data=self.request.POST or None
                )
            }
            
            
        self.form_cadastro=self.contexto['form_cadastro']
        self.perfil_cadastro=self.contexto['perfil_cadastro']
        
        if self.request.user.is_authenticated:
            self.template_name='cadastro_de_usuarios/cadastro_update.html'
            
            
        self.renderizar=render(self.request,self.template_name,self.contexto)
        
    def get(self,*args, **kwargs):
        return self.renderizar
    



class CriarUser(BaseCadastro,oficial_merg):
    def post(self,*args, **kwargs):
        if not self.form_cadastro.is_valid() or not self.perfil_cadastro.is_valid():
            return self.renderizar
        
        
        password=self.form_cadastro.cleaned_data.get('password')
        
        
        usuario=self.form_cadastro.save(commit=False)
        usuario.set_password(password)
        usuario.save()
        
        perfil=self.perfil_cadastro.save(commit=False)
        perfil.usuario=usuario
        perfil.save()
        
        
        if not self.request.session.session_key:
            self.request.session.save()
            
        old_session_key=self.request.session.session_key
        
        if password:
            autentica=authenticate(
                self.request,
                username=usuario,
                password=password
            )
            
            if autentica:
                login(self.request,user=usuario)
                
                merge=oficial_merg()
                merge.marge_cards(old_session_key,usuario)
                
        messages.success(self.request,'Sucesso ao criar sua conta, aproveite suas comprar.')
        
        return redirect('index:index')
    
    
    
class Atualizauser(BaseCadastro):
    def post(self,*args, **kwargs):
        if not self.form_cadastro.is_valid() or not self.perfil_cadastro.is_valid():
            return self.renderizar
        
        username=self.form_cadastro.cleaned_data.get('username')
        password=self.form_cadastro.cleaned_data.get('password')
        email=self.form_cadastro.cleaned_data.get('email')
        first_name=self.form_cadastro.cleaned_data.get('first_name')
        last_name=self.form_cadastro.cleaned_data.get('last_name')
        
        if self.request.user.is_authenticated:
            usuario=get_object_or_404(
                User,pk=self.request.user.pk
            )
            
            usuario.username=username
            
            if password:
                usuario.set_password(password)
                
                
            usuario.email=email
            usuario.first_name=first_name
            usuario.last_name=last_name
            usuario.save()
            self.request.user=usuario
            
            
            if not self.perfil:
                self.perfil_cadastro.cleaned_data['usuario']=usuario
                perfil=Perfil(**self.perfil_cadastro.cleaned_data)
                perfil.save()
                
            else:
                perfil=self.perfil_cadastro.save(commit=False)
                perfil.usuario=usuario
                perfil.save()
                
            if password:
                autentica=authenticate(
                    self.request,
                    usarneme=usuario,
                    password=password
                )
                
                if autentica:
                    login(self.request,user=usuario)
                    
            messages.success(self.request,'Sucesso ao atualizar seus dados cadastrados.')
            
            return redirect('index:index')

            
            