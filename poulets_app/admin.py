from django.contrib import admin

# Register your models here.
from .models import (
    Ferme, Batiment, Gamme, Employe, Veterinaire, Client, Fournisseur,
    Lot, Stock, Achat, Vente, Bande, Deces, Medicament
)

# Enregistre chaque modèle pour visualisation/crud
admin.site.register(Ferme)
admin.site.register(Batiment)
admin.site.register(Gamme)
admin.site.register(Employe)
admin.site.register(Veterinaire)
admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Lot)
admin.site.register(Stock)
admin.site.register(Achat)
admin.site.register(Vente)
admin.site.register(Bande)
admin.site.register(Deces)
admin.site.register(Medicament)