from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib import messages
from django.shortcuts import render,redirect


class login_class(View):
    def get(self,request):
        form=AuthenticationForm()
        return render(request,'cadastro_de_usuarios/login.html',{'form_cadastro':form})
    
    def post(self,request):
        form=AuthenticationForm(self.request,data=self.request.POST)
        
        if form.is_valid():
            
            user=form.get_user()
            
            if not request.session.session_key:
                request.session.save()
                
            old_session_key=request.session.session_key
                
            login(request,user)
                
            messages.success(request,'Secesso ao fazer login.')
            return redirect('index:index')
            
        messages.error(request,'Erro ao tentar fazer o login. Tente novamente.')
            
        return render(request,'cadastro_de_usuarios/login.html', {'form_cadastro':form})
    
    
class logout_class(View):
    def get(self,*args, **kwargs):
        logout(self.request)
        return redirect('index:index')   