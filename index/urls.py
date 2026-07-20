from django.urls import path
from .views.index_views import Indexview
from .views import view_institucional

app_name='index'

urlpatterns = [
    path('',Indexview.as_view(),name='index'),
    path('contato/',view_institucional.contatoview.as_view(),name='contato'),
    path('politica de privacidade/',view_institucional.politicaprivacidade.as_view(),name='politica de privacidade'),
    path('politica de troca/',view_institucional.politicatroca.as_view(),name='politica de troca'),
    path('sobre/',view_institucional.sobre.as_view(),name='sobre'),
    path('termo de uso/',view_institucional.termodeuso.as_view(),name='termo de uso'),
]