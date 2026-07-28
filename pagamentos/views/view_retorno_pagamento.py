from django.shortcuts import render
from django.views import View


class RetornoPagamento(View):
    def get(self,request):
        reference=request.GET.get('reference')
        status=request.GET.get('status','pending')
        sucesso=status in ['3','paid']
        
        context={
            'reference':reference,
            'status':status,
            'success':sucesso
        }
        
        return render(request,'pagamentos/return.html',context)
        