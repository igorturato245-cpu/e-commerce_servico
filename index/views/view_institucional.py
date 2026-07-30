from django.shortcuts import render,redirect
from django.views import View
from index.models import Contato

class contatoview(View):
    def get(self,request):
        return render(request, 'contato.html') 
    
    def post(self,request):
        nome=request.POST.get('Nome') 
        email=request.POST.get('Email')
        texto=request.POST.get('Área de contato')  
        
        Contato.objects.create(
            nome=nome,
            email=email,
            texto=texto
        )
        
        return redirect('index:index')
        
    
class politicaprivacidade(View):
    def get(self,request):
        return render(request, 'politica-privacidade.html')
    
class politicatroca(View):
    def get(self,request):
        return render(request, 'politica-troca.html')    
    
class sobre(View):
    def get(self,request):
        return render(request, 'sobre.html')    
    
class termodeuso(View):
    def get(self,request):
        return render(request, 'termo-uso.html')
    
