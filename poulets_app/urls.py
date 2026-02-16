from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
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
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]




from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Authentification
    path('login/', LoginView.as_view(template_name='poulets_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Bandes
    path('bandes/', views.BandeListView.as_view(), name='bande-list'),
    path('bande/<int:pk>/', views.BandeDetailView.as_view(), name='bande-detail'),
    path('bande/nouvelle/', views.BandeCreateView.as_view(), name='bande-create'),

    # Stocks
    path('stocks/', views.StockListView.as_view(), name='stock-list'),

    # Ventes
    path('ventes/', views.VenteListView.as_view(), name='vente-list'),

    # Mortalités
    path('deces/', views.DecesListView.as_view(), name='deces-list'),

    # Catalogue & commandes client
    path('catalogue/', views.CatalogueView.as_view(), name='catalogue'),
    path('mes-commandes/', views.MesCommandesView.as_view(), name='mes_commandes'),

    # Profil
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Support & Rapports
    path('support/', views.SupportView.as_view(), name='support'),
    path('rapport-rendement/', views.RapportRendementView.as_view(), name='rapport_rendement'),
]