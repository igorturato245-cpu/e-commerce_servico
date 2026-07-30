
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from cadastro_de_usuarios.models import Endereco_usuario
from django.shortcuts import get_object_or_404,render,redirect
from django.contrib import messages



class Lista_end(LoginRequiredMixin,View):
    template_name='cadastro_de_usuarios/lista_end.html'
    
    def get(self,request,*args, **kwargs):
        
        enderecos=Endereco_usuario.objects.filter(usuario=self.request.user).order_by('-padrao','-id')
        
        return render(self.request,self.template_name,{'enderecos':enderecos})
    

class Delete_end(LoginRequiredMixin,View):
    def post(self,request,pk,*args, **kwargs):
        
        
        endereco=get_object_or_404(Endereco_usuario,pk=pk,usuario=self.request.user)
        
        endereco.delete()
        
        messages.success(self.request,'Secesso ao deletar endereço, boas compras.')
        
        return redirect('index:index')
    

class Default_end(LoginRequiredMixin,View):
    def post(self,request,pk,*args, **kwargs):
                        
        enderecopadrao=get_object_or_404(Endereco_usuario,pk=pk,usuario=self.request.user)
        
        enderecopadrao.padrao=True
        enderecopadrao.save()
        
        messages.success(self.request,'Secesso ao alterar endereço padrão, boas comprars.')
        
        return redirect('index:index')