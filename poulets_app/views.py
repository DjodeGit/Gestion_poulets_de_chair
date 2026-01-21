from pyexpat.errors import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Bande, Pesee, Mortalite, Alimentation,Stock,Vente,ProduitVente
from django.contrib.auth.decorators import login_required
import datetime

from poulets_app import models

# Create your views here.
def test_base(request):
    return render(request, 'poulets_app/base.html')
def dashboard(request):
    return render(request, 'poulets_app/base.html')

# Accueil (teste base.html)


# Dashboard (interne)
@login_required
def dashboard(request):
    if request.user.role not in ['admin', 'employe']:
        return redirect('login')  # ou '/login/'
    
    context = {
        'user': request.user,
    }
    return render(request, 'poulets_app/dashboard.html', context)
# Liste bandes (interne)
class BandeListView(LoginRequiredMixin, ListView):
    model = Bande
    template_name = 'poulets_app/bande_list.html'
    context_object_name = 'bandes'
    paginate_by = 12
    ordering = ['-date_arrivee']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        statut = self.request.GET.get('statut')

        if q:
            qs = qs.filter(
                numero__icontains=q
            ) | qs.filter(
                gamme__nom__icontains=q
            ) | qs.filter(
                batiment__nom__icontains=q
            )
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        for bande in context['bandes']:
            if bande.date_arrivee:
                bande.age_jours = (today - bande.date_arrivee).days
            else:
                bande.age_jours = 0
        return context
    def bande_list(request):
        if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
            return HttpResponseRedirect('/login/')
        return render(request, 'poulets_app/bande_list.html', {'title': 'Bandes'})

# Liste stocks (interne)
class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'poulets_app/stock_list.html'
    context_object_name = 'articles'
    ordering = ['nom']
    def stock_list(request):
        if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
            return HttpResponseRedirect('/login/')
        return render(request, 'poulets_app/stock_list.html', {'title': 'Stocks'})

class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'poulets_app/stock_detail.html'
    context_object_name = 'article'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object

        # Historique des 30 derniers jours pour le graphique
        from django.utils import timezone
        from datetime import timedelta
        debut = timezone.now() - timedelta(days=30)
        mouvements = article.mouvements.filter(date__gte=debut).order_by('date')

        context['mouvements_recents'] = mouvements
        context['graphique_data'] = {
            'labels': [m.date.strftime('%d/%m') for m in mouvements],
            'quantites': []
        }
        # Recalculer le stock jour par jour
        stock_courant = article.quantite_actuelle
        quantites = []
        for m in reversed(mouvements):
            if m.type_mouvement == 'entree':
                stock_courant -= m.quantite
            else:
                stock_courant += m.quantite
            quantites.insert(0, float(stock_courant))
        quantites.append(float(article.quantite_actuelle))
        context['graphique_data']['quantites'] = quantites

        return context

# Liste ventes (interne)
# views.py
class VenteListView(LoginRequiredMixin, ListView):
    model = Vente
    template_name = 'poulets_app/vente_list.html'
    context_object_name = 'ventes'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        statut = self.request.GET.get('statut')
        if q:
            qs = qs.filter(
                models.Q(numero__icontains=q) |
                models.Q(client_nom__icontains=q) |
                models.Q(client_telephone__icontains=q)
            )
        if statut:
            qs = qs.filter(statut=statut)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ventes_mois'] = Vente.objects.filter(
            date_vente__month=datetime.date.today().month,
            statut__in=['confirmee', 'payee']
        ).aggregate(t=models.Sum('montant_total'))['t'] or 0
        return context
    def vente_list(request):
        if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
            return HttpResponseRedirect('/login/')
        return render(request, 'poulets_app/vente_list.html', {'title': 'Ventes'})

# Liste décès/santé (interne)
# poulets_app/views.py → ajoute ça

class DecesListView(LoginRequiredMixin, ListView):
    model = Mortalite
    template_name = 'poulets_app/deces_list.html'
    context_object_name = 'deces'
    paginate_by = 20
    ordering = ['-date', '-cree_le']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        bande_id = self.request.GET.get('bande')
        cause = self.request.GET.get('cause')

        if q:
            qs = qs.filter(
                
                models.Q(bande__numero__icontains=q) |
                models.Q(bande__gamme__nom__icontains=q)
            )
        if bande_id:
            qs = qs.filter(bande_id=bande_id)
        if cause:
            qs = qs.filter(cause=cause)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum
        today = datetime.date.today()
        
        context['total_mois'] = Mortalite.objects.filter(
            date__month=today.month,
            date__year=today.year
        ).aggregate(total=Sum('nombre'))['total'] or 0

        context['total_aujourdhui'] = Mortalite.objects.filter(date=today).aggregate(total=Sum('nombre'))['total'] or 0
        
        context['bandes'] = Bande.objects.filter(statut='en_croissance')
    
# Rapport rendement (interne)
def rapport_rendement(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/rapport_rendement.html', {'title': 'Rapport Rendement'})

# Logout
def logout_view(request):
    auth_logout(request) # type: ignore
    messages.success(request, 'Déconnexion réussie.')
    return HttpResponseRedirect('/login/')

# Vues client (exemples pour conditional nav)


def mes_commandes(request):
    if not request.user.is_authenticated or request.user.role != 'client':
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/mes_commandes.html', {'title': 'Mes Commandes'})

def support(request):
    return render(request, 'poulets_app/support.html', {'title': 'Support'})

# Login stub (à développer)
def login_view(request):
    return render(request, 'poulets_app/login.html', {'title': 'Connexion'})

# Inscription client stub
def inscription_client(request):
    return render(request, 'poulets_app/inscription_client.html', {'title': 'Inscription'})
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

class CatalogueView(LoginRequiredMixin, ListView):
    template_name = 'poulets_app/catalogue.html'
    context_object_name = 'bandes'

    def get_queryset(self):
        return Bande.objects.filter(statut='prete').order_by('-date_arrivee')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['produits_transformes'] = ProduitVente.objects.filter(en_stock=True)

        # Calcul de la mortalité totale pour chaque bande
        for bande in context['bandes']:
            total = bande.mortalite_set.aggregate(total=Sum('nombre'))['total']
            bande.mortalite_totale = total or 0

            # Poids moyen (dernière pesée)
            last_pesee = bande.pesee_set.last()
            bande.poids_moyen = last_pesee.poids_moyen if last_pesee else 0

        return context