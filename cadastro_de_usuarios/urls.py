from django.urls import path
from cadastro_de_usuarios.views.cadastro_view import CriarUser, Atualizauser
from cadastro_de_usuarios.views.login_view import login_class,logout_class
from cadastro_de_usuarios.views.criar_end_view import Criarend,Atualizarend
from cadastro_de_usuarios.views.lista_ends_view import Lista_end,Delete_end,Default_end


app_name='cadastro_login'


urlpatterns = [
    path('',CriarUser.as_view(),name='cadastro'),
    path('atualizar/cadastro/', Atualizauser.as_view(),name='atualizar_cadastro'),
    path('login/',login_class.as_view(),name='login'),
    path('logout/', logout_class.as_view(),name='logout'),
    path('criar/endereco/',Criarend.as_view(),name='criar_end'),
    path('atualizar/endereco/<int:pk>/',Atualizarend.as_view(),name='atualizar_end'),
    path('lista/endereco',Lista_end.as_view(),name='lista_ends'),
    path('deletar/<int:pk>',Delete_end.as_view(),name='delete_end'),
    path('padrao/<int:pk>',Default_end.as_view(),name='end_padrao')
]
