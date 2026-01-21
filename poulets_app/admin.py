from django.contrib import admin

# Register your models here.
from .models import (
    Ferme, Batiment, Gamme, Employe, Veterinaire, Client, Fournisseur,
    Lot, Stock, Achat, Vente, Bande, Mortalite
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
admin.site.register(Mortalite)
#admin.site.register(Medicament)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# ENREGISTRE TON MODÈLE USER PERSONNALISÉ DANS L'ADMIN
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle DjodeSync', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rôle DjodeSync', {'fields': ('role',)}),
    )