from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_base, name='test_base'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bandes/', views.bande_list, name='bande_list'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('ventes/', views.vente_list, name='vente_list'),
    path('sante/', views.deces_list, name='deces_list'),
    path('rapports/rendement/', views.rapport_rendement, name='rapport_rendement'),
    path('logout/', views.logout_view, name='logout'),
    # Vues client
    path('catalogue/', views.catalogue, name='catalogue'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('support/', views.support, name='support'),
    path('login/', views.login_view, name='login'),
    path('inscription-client/', views.inscription_client, name='inscription_client'),
]