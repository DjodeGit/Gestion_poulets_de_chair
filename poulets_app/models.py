from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
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
    duree_cycle = models.PositiveIntegerField(default=42)  # jours

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

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)

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

    nom = models.CharField(max_length=100, verbose_name="Nom de l'article",default='Article sans nom',blank=True,)
    type_aliment = models.CharField(max_length=20, choices=TYPE_ALIMENT, default='autre')
    quantite_actuelle = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock actuel")
    unite = models.CharField(max_length=10, default="kg", choices=[('kg','kg'), ('sac','sac'), ('litre','litre')])
    seuil_alerte = models.DecimalField(max_digits=10, decimal_places=2, default=100, verbose_name="Seuil alerte")

    cree_le = models.DateTimeField(default=timezone.now, editable=False,null=True, blank=True)
    modifie_le = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Article en stock"
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

class Vente(models.Model):
    date = models.DateField(auto_now_add=True)
    quantite_vendue = models.PositiveIntegerField()
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    bande = models.ForeignKey('Bande', on_delete=models.PROTECT, related_name='ventes')

class Bande(models.Model):
    STATUT_CHOICES = [('croissance', 'En Croissance'), ('prete', 'Prête'), ('vendue', 'Vendue')]
    date_arrivee = models.DateField()
    nb_poulets_init = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='croissance')
    gamme = models.ForeignKey(Gamme, on_delete=models.PROTECT)
    batiment = models.ForeignKey(Batiment, on_delete=models.PROTECT)
    employe_responsable = models.ManyToManyField(Employe, blank=True, related_name='bandes')

    def rendement(self):
        total_deces = self.deces.aggregate(total=models.Sum('nb_deces'))['total'] or 0
        return (self.nb_poulets_init - total_deces) * 100 / self.nb_poulets_init if self.nb_poulets_init > 0 else 0

    def __str__(self):
        return f"Bande {self.id} - {self.nb_poulets_init} poulets ({self.statut})"

class Deces(models.Model):
    date = models.DateField()
    nb_deces = models.PositiveIntegerField(default=1)
    cause = models.CharField(max_length=200, blank=True)
    bande = models.ForeignKey(Bande, on_delete=models.CASCADE, related_name='deces')

class Medicament(models.Model):
    nom = models.CharField(max_length=100)
    dosage = models.DecimalField(max_digits=5, decimal_places=2)
    date_admin = models.DateField(auto_now_add=True)
    bande = models.ForeignKey(Bande, on_delete=models.CASCADE, related_name='medicaments')
    veterinaire = models.ForeignKey(Veterinaire, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.nom} pour Bande {self.bande.id}"
class Pesee(models.Model):
    """
    Pesée quotidienne ou hebdomadaire d'une bande
    """
    bande = models.ForeignKey(
        'Bande',
        on_delete=models.CASCADE,
        related_name='pesee_set',
        verbose_name="Bande"
    )
    
    date = models.DateField(
        verbose_name="Date de pesée",
        help_text="Date à laquelle la pesée a été effectuée"
    )
    
    poids_moyen = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Poids moyen (kg)",
        help_text="Exemple : 1.850 kg"
    )
    
    nombre_poulets_peses = models.PositiveIntegerField(
        default=100,
        verbose_name="Nombre de poulets pesés",
        help_text="Échantillon représentatif (minimum 100 recommandé)"
    )
    
    homogeneite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Homogénéité (%)",
        help_text="Coefficient de variation. Optionnel, calculable automatiquement plus tard"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Observations",
        help_text="Commentaires sur la pesée (santé, stress, etc.)"
    )
    
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pesée"
        verbose_name_plural = "Pesées"
        ordering = ['-date']
        unique_together = ('bande', 'date')  # une seule pesée par jour et par bande

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.poids_moyen} kg"

    def save(self, *args, **kwargs):
        # Optionnel : arrondir à 3 décimales
        if self.poids_moyen:
            self.poids_moyen = round(self.poids_moyen, 3)
        super().save(*args, **kwargs)

class Mortalite(models.Model):
    """
    Mortalité quotidienne d'une bande
    """
    bande = models.ForeignKey(
        'Bande',
        on_delete=models.CASCADE,
        related_name='mortalite_set',
        verbose_name="Bande"
    )
    
    date = models.DateField(
        verbose_name="Date",
        help_text="Date du relevé de mortalité"
    )
    
    nombre = models.PositiveIntegerField(
        verbose_name="Nombre de morts",
        help_text="Nombre de poulets morts ce jour"
    )
    
    CAUSE_CHOICES = [
        ('maladie', 'Maladie'),
        ('chaleur', 'Chaleur / Stress thermique'),
        ('froid', 'Froid'),
        ('asphyxie', 'Asphyxie'),
        ('ecrasement', 'Écrasement'),
        ('cannibalisme', 'Cannibalisme'),
        ('autre', 'Autre / Inconnu'),
    ]
    
    cause = models.CharField(
        max_length=20,
        choices=CAUSE_CHOICES,
        default='autre',
        verbose_name="Cause principale"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Observations",
        help_text="Symptômes observés, traitement appliqué, etc."
    )
    
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mortalité"
        verbose_name_plural = "Mortalités"
        ordering = ['-date']
        unique_together = ('bande', 'date')  # une seule saisie par jour

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.nombre} morts ({self.get_cause_display})"

class Alimentation(models.Model):
    """
    Consommation d'aliment par bande
    """
    bande = models.ForeignKey(
        'Bande',
        on_delete=models.CASCADE,
        related_name='alimentation_set',
        verbose_name="Bande"
    )
    
    date = models.DateField(
        verbose_name="Date de distribution"
    )
    
    type_aliment = models.CharField(
        max_length=50,
        verbose_name="Type d'aliment",
        help_text="Ex: Démarrage, Croissance, Finition, Pré-finition"
    )
    
    quantite_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Quantité distribuée (kg)"
    )
    
    stock_provenance = models.ForeignKey(
        'Stock',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='alimentations',
        verbose_name="Provenance stock"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="Remarques"
    )
    
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Alimentation"
        verbose_name_plural = "Alimentations"
        ordering = ['-date']
        unique_together = ('bande', 'date', 'type_aliment')

    def __str__(self):
        return f"{self.bande} – {self.date} : {self.quantite_kg} kg {self.type_aliment}"




class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('employe', 'Employé'),
        ('client', 'Client'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Rôle"
    )

    # On désactive proprement les relations inverses pour éviter tout clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='+',      # pas de relation inverse = zéro risque de clash
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='+',      # même chose
        blank=True,
    )

    def __str__(self):
        return self.username

# === 1. ACHAT & APPROVISIONNEMENT ===
class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)

    def __str__(self): return self.nom

class CommandeFournisseur(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT)
    date_commande = models.DateField(auto_now_add=True)
    date_livraison_prevue = models.DateField()
    statut = models.CharField(max_length=20, choices=[
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('recue', 'Reçue'),
    ], default='brouillon')
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

# === 2. VENTES & MARKETING ===
class ProduitVente(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix_kg = models.DecimalField(max_digits=8, decimal_places=2)
    en_stock = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='produits/', blank=True)

    def __str__(self): return self.nom

class CommandeClient(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    client_nom = models.CharField(max_length=100)
    client_telephone = models.CharField(max_length=20)
    produits = models.ManyToManyField(ProduitVente, through='LigneCommande')
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('livree', 'Livrée'),
    ], default='en_attente')

class LigneCommande(models.Model):
    commande = models.ForeignKey(CommandeClient, on_delete=models.CASCADE)
    produit = models.ForeignKey(ProduitVente, on_delete=models.PROTECT)
    quantite_kg = models.DecimalField(max_digits=8, decimal_places=2)