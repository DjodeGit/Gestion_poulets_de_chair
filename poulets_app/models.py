from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# ==================== USER PERSONNALISÉ ====================
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('employe', 'Employé'),
        ('client', 'Client'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employe', verbose_name="Rôle")

    # Évite le clash avec auth.User
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)

    def __str__(self):
        return self.username

# ==================== MODELES DE BASE ====================
class Ferme(models.Model):
    nom = models.CharField(max_length=100)
    localisation = models.CharField(max_length=200, blank=True)
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Batiment(models.Model):
    nom = models.CharField(max_length=50)
    capacite_max = models.PositiveIntegerField(default=10000, validators=[MinValueValidator(1)])
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='batiments')

    def __str__(self):
        return f"{self.nom} ({self.ferme.nom})"

class Gamme(models.Model):
    type_poulet = models.CharField(max_length=50, default='broiler')
    poids_cible = models.DecimalField(max_digits=5, decimal_places=2, default=2.5)
    duree_cycle = models.PositiveIntegerField(default=42)

    def __str__(self):
        return f"{self.type_poulet} - {self.poids_cible}kg"

class Employe(models.Model):
    nom = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='employe')
    ferme = models.ForeignKey(Ferme, on_delete=models.CASCADE, related_name='employes')

    def __str__(self):
        return f"{self.nom} ({self.role})"

class Veterinaire(models.Model):
    nom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nom

class Client(models.Model):
    nom = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    type_client = models.CharField(max_length=20, default='particulier')

    def __str__(self):
        return self.nom

# ==================== APPROVISIONNEMENT ====================
class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class Lot(models.Model):
    TYPE_CHOICES = [('provende', 'Provende'), ('medicament', 'Médicament')]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    date_expiry = models.DateField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name='lots')

    def __str__(self):
        return f"{self.type} - {self.quantite} ({self.fournisseur.nom})"

class Stock(models.Model):
    TYPE_ALIMENT = [
        ('demarrage', 'Démarrage'),
        ('croissance', 'Croissance'),
        ('finition', 'Finition'),
        ('pre_finition', 'Pré-finition'),
        ('medicament', 'Médicament'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, default='Article sans nom')
    type_aliment = models.CharField(max_length=20, choices=TYPE_ALIMENT, default='autre')
    quantite_actuelle = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unite = models.CharField(max_length=10, default="kg", choices=[('kg','kg'), ('sac','sac'), ('litre','litre')])
    seuil_alerte = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    cree_le = models.DateTimeField(default=timezone.now)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_aliment_display()})"

    def est_en_rupture(self):
        return self.quantite_actuelle <= self.seuil_alerte
    est_en_rupture.boolean = True

class Achat(models.Model):
    date = models.DateField(auto_now_add=True)
    quantite_achetee = models.PositiveIntegerField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)

# ==================== PRODUCTION ====================
class Bande(models.Model):
    STATUT_CHOICES = [('croissance', 'En Croissance'), ('prete', 'Prête'), ('vendue', 'Vendue')]
    date_arrivee = models.DateField()
    nb_poulets_init = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='croissance')
    gamme = models.ForeignKey(Gamme, on_delete=models.PROTECT)
    batiment = models.ForeignKey(Batiment, on_delete=models.PROTECT)
    employe_responsable = models.ManyToManyField(Employe, blank=True, related_name='bandes')

    def __str__(self):
        return f"Bande {self.id} - {self.nb_poulets_init} poulets ({self.statut})"

class Pesee(models.Model):
    bande = models.ForeignKey(Bande, on_delete=models.CASCADE, related_name='pesee_set')
    date = models.DateField()
    poids_moyen = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    nombre_poulets_peses = models.PositiveIntegerField(default=100)
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bande', 'date')

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.poids_moyen} kg"

class Mortalite(models.Model):
    bande = models.ForeignKey(Bande, on_delete=models.CASCADE, related_name='mortalite_set')
    date = models.DateField()
    nombre = models.PositiveIntegerField()
    cause = models.CharField(max_length=20, choices=[
        ('maladie', 'Maladie'), ('chaleur', 'Chaleur'), ('froid', 'Froid'),
        ('asphyxie', 'Asphyxie'), ('ecrasement', 'Écrasement'), ('cannibalisme', 'Cannibalisme'), ('autre', 'Autre')
    ], default='autre')
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bande', 'date')

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.nombre} morts"

class Alimentation(models.Model):
    bande = models.ForeignKey(Bande, on_delete=models.CASCADE, related_name='alimentation_set')
    date = models.DateField()
    type_aliment = models.CharField(max_length=50)
    quantite_kg = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    stock_provenance = models.ForeignKey(Stock, null=True, blank=True, on_delete=models.SET_NULL, related_name='alimentations')
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bande', 'date', 'type_aliment')

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.quantite_kg} kg {self.type_aliment}"

# ==================== VENTES ====================
class Vente(models.Model):
    date = models.DateField(auto_now_add=True)
    quantite_vendue = models.PositiveIntegerField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    bande = models.ForeignKey(Bande, on_delete=models.PROTECT, related_name='ventes')

    def __str__(self):
        return f"Vente {self.id} – {self.quantite_vendue} poulets"

# ==================== PRODUITS TRANSFORMÉS (SANS PHOTO POUR L'INSTANT) ====================
class ProduitVente(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix_kg = models.DecimalField(max_digits=8, decimal_places=2)
    en_stock = models.BooleanField(default=True)
    # photo = models.ImageField(upload_to='produits/', blank=True, null=True)  
    class Meta:
        verbose_name = "Produit en vente"
        verbose_name_plural = "Produits en vente"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.prix_kg} FCFA/kg"