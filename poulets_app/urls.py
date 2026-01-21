from django.urls import path
from . import views
from .views import BandeListView,StockListView,StockDetailView,VenteListView,DecesListView,CatalogueView

urlpatterns = [
    path('', views.test_base, name='test_base'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('bandes/', BandeListView.as_view(), name='bande-list'),
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stock/<int:pk>/', StockDetailView.as_view(), name='stock-detail'),
    path('ventes/', VenteListView.as_view(), name='vente-list'),
    path('deces/', DecesListView.as_view(), name='deces-list'),
    path('rapports/rendement/', views.rapport_rendement, name='rapport_rendement'),
    path('logout/', views.logout_view, name='logout'),
    # Vues client
    path('catalogue/', CatalogueView.as_view(), name='catalogue'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('support/', views.support, name='support'),
    path('login/', views.login_view, name='login'),
    path('inscription-client/', views.inscription_client, name='inscription_client'),
    path('profile/', views.dashboard, name='profile'),
]