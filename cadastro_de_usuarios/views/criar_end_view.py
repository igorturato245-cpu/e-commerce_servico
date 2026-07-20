from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.contrib import messages
from cadastro_de_usuarios.models import Endereco_usuario
from cadastro_de_usuarios.forms import EnderecoForm
from django.views import View


class Enderecoview(LoginRequiredMixin,View):
    
    def setup(self,request,*args, **kwargs):
        super().setup(request,*args, **kwargs)
        
        
        pk=self.kwargs.get('pk')
        
        self.endereco=Endereco_usuario.objects.filter(
            usuario=self.request.user,
            pk=pk
        ).first()
        
        if self.endereco:
            self.template_name='cadastro_de_usuarios/atualizar_end.html'
            form=EnderecoForm(
                data=self.request.POST or None,
                instance=self.endereco
            )
            
        else:
            self.template_name='cadastro_de_usuarios/endereco.html'
            form=EnderecoForm(
                data=self.request.POST or None
            )
            
        self.contexto={'endereco_form':form}
        self.form_end=self.contexto['endereco_form']
        
            
        self.renderizar=render(self.request,self.template_name,self.contexto)
        
    def get(self,*args, **kwargs):
        return self.renderizar
    
    
class Criarend(Enderecoview,View):
    def post(self,*args, **kwargs):
        if not self.form_end or not self.form_end.is_valid():
            messages.error(self.request,'Erro ao criar endereço, tente novamente')
            return render(self.request,self.template_name,self.contexto)
        
        endereco=self.form_end.save(commit=False)
        endereco.usuario=self.request.user
        endereco.save()
        
        messages.success(self.request,'Sucesso ao criar o endereço, boas compras.')
        
        return redirect('index:index')
    
    
class Atualizarend(Enderecoview,View):
    def post(self,*args, **kwargs):
        form=self.form_end
        if not form or not form.is_valid():
            messages.error(self.request,'Erro ao atualizar endereço, tente novamente.')
            return render(self.request,self.template_name,self.contexto)
        
        endereco_atualizado=form.save(commit=False)
        endereco_atualizado.usuario=self.request.user
        endereco_atualizado.save()
        
        
        messages.success(self.request,'Secesso ao atualizar endereço, boas compras.')
        
        return redirect('index:index')        

