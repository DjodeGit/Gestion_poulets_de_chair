from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
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
    quantite_dispo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_min = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    lot = models.OneToOneField(Lot, on_delete=models.CASCADE, related_name='stock')

    def est_en_rupture(self):
        return self.quantite_dispo < self.seuil_min

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
