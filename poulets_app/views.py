from django.shortcuts import render

# Create your views here.

def test_base(request):
    return render(request, 'poulets_app/base.html')
def dashboard(request):
    return render(request, 'poulets_app/base.html')

# Accueil (teste base.html)


# Dashboard (interne)
def dashboard(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')  # Redirige si non autorisé
    return render(request, 'poulets_app/dashboard.html', {'title': 'Dashboard'})

# Liste bandes (interne)
def bande_list(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/bande_list.html', {'title': 'Bandes'})

# Liste stocks (interne)
def stock_list(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/stock_list.html', {'title': 'Stocks'})

# Liste ventes (interne)
def vente_list(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/vente_list.html', {'title': 'Ventes'})

# Liste décès/santé (interne)
def deces_list(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/deces_list.html', {'title': 'Santé/Décès'})

# Rapport rendement (interne)
def rapport_rendement(request):
    if not request.user.is_authenticated or request.user.role not in ['employé', 'admin']:
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/rapport_rendement.html', {'title': 'Rapport Rendement'})

# Logout
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return HttpResponseRedirect('/login/')

# Vues client (exemples pour conditional nav)
def catalogue(request):
    if not request.user.is_authenticated or request.user.role != 'client':
        return HttpResponseRedirect('/login/')
    return render(request, 'poulets_app/catalogue.html', {'title': 'Catalogue'})

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