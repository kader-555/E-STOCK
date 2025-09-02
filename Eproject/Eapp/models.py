from django.db import models
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib.auth.models import AbstractUser
# ----------Custom User Model----------
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1 , 'client'),
        (2,'admin')
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username

# -------------Models-------------
# Client Model 
class Client(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    montantImpayee = models.FloatField(default=0.0)
    image = models.ImageField(upload_to='clients/', null=True, blank=True)

    def __str__(self):
        return f"Client: {self.nom} ({self.telephone})"

    def ajouterProduitAuPanier(self,produit,quantite):
        if produit.quantiteDisponible >= quantite : 
            panier, created = Panier.objects.get_or_create(client = self)
            ligne_commande = LigneCommande.objects.create(
                commande = None,
                produit = produit , 
                quantite = quantite , 
                panier = panier , 
                prixUnitaire = produit.prix 
            )
            produit.quantiteDisponible -= quantite
            produit.save()
            panier.save()
            return ligne_commande 
        else : 
            raise ValueError("Quantité insuffisante en stock")


    def passerCommande(self,panier):
        if panier.produits.count()==0:
            raise ValueError('Le panier est vide')
        else :
            commande = Commande.objects.create(
                client = self,
                statut = 'En cours'
        )   
            for ligne in panier.lignecommande_set.all():
                ligne.commande = commande 
                ligne.panier = None 
                ligne.save()
                panier.produits.remove(ligne.produit)
                panier.save()
            return commande 
            
        

    def parcourirProduits(self):
        return Produit.objects.all()

    def effectuerPaiement(self):
        pass

# Fournisseur Model
class Fournisseur(models.Model):
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    pays = models.CharField(max_length=50)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100, unique = True)
    modeLivraison = models.CharField(max_length=50)
    image = models.ImageField(upload_to='fournisseurs/', null=True, blank=True)

    def __str__(self):
        return f"Fournisseur: {self.nom} ({self.email})"

# Produit Model
class Produit(models.Model):
    nom = models.CharField(max_length=100)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    prix = models.FloatField()
    quantiteDisponible = models.IntegerField()
    seuilStock = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='produits/', null=True, blank=True)

    def __str__(self):
        return f"Produit: {self.nom} (Fournisseur: {self.fournisseur.nom})"

# Commande Model
class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50)

    def __str__(self):
        return f"Commande: {self.id} (Client: {self.client.nom} , Date:{self.date})"
    @property
    def montantTotal(self):
        total = 0
        for ligne in self.lignecommande_set.all():
            total += ligne.quantite * ligne.prixUnitaire
            
        return total 

# Entrepôt Model
class Entrepot(models.Model):
    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    capaciteMaximale = models.IntegerField()
    quantiteActuelle = models.IntegerField()
    localisationGeographique = models.CharField(max_length=100)
    image = models.ImageField(upload_to='entrepots/', null=True, blank=True)

    def __str__(self):
        return f"Entrepot: {self.nom} ({self.adresse})"

    @property
    def suivreCapacite(self):
        if self.quantiteActuelle > self.capaciteMaximale :
            raise ValueError("Capacité maximale dépassée")
        else : 
            return (self.quantiteActuelle / self.capaciteMaximale) * 100

# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    nom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=50)
    image = models.ImageField(upload_to='admins/', null=True, blank=True)

    def __str__(self):
        return f"Admin: {self.nom} ({self.role})"
    
# LigneCommande Model (intermediate for Commande/Produit)
class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, null=True, blank=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    panier =models.ForeignKey('Panier', on_delete=models.CASCADE, null=True, blank=True)
    prixUnitaire = models.FloatField()

    def __str__(self):
        commande_part = f"Commande: {self.commande.id}" if self.commande_id else "Commande: None"
        return f"LigneCommande: {self.id} ({commande_part}, Produit: {self.produit.nom})"

# Panier Model
class Panier(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    produits = models.ManyToManyField(Produit, through='LigneCommande')

    def __str__(self):
        return f"Panier: {self.id} (Client: {self.client.nom})"


    def supprimerProduit(self,produit):
        ligne = LigneCommande.objects.filter(panier = self , produit = produit).first()
        if ligne :
            produit.quantiteDisponible += ligne.quantite 
            produit.save()
            ligne.delete()
            self.produits.remove(produit)
            self.save()
        else : 
            raise ValueError("Le produit n'est pas dans le panier") 

    def viderPanier(self):
        self.lignecommande_set.all().delete()
        self.produits.clear()
        self.save()

# Facture Model
class Facture(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    dateEmission = models.DateTimeField(auto_now_add=True)
    montantTotal = models.FloatField()
    statutPaiement = models.CharField(max_length=50)

    def __str__(self):
        return f"Facture: {self.id} (Commande: {self.commande.id})"

    def genererPDF(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{self.id}.pdf"'
        p = canvas.Canvas(response)
        p.drawString(100, 750, f"Facture #{self.id}")
        p.drawString(100, 730, f"Commande: {self.commande.id}")
        p.drawString(100, 710, f"Montant Total: {self.commande.montantTotal}")
        p.drawString(100, 690, f"Statut Paiement: {self.statutPaiement}")
        y = 670
        for ligne in self.commande.lignecommande_set.all():
            p.drawString(100, y, f"Produit: {ligne.produit.nom}, Qty: {ligne.quantite}")
            y -= 20
        p.showPage()
        p.save()
        return response
            
# Paiement Model
class Paiement(models.Model):
    id = models.AutoField(primary_key=True)
    montant = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    modePaiement = models.CharField(max_length=50)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE)

    def __str__(self):
        return f"Paiement: {self.id} (Montant: {self.montant})"

    def effectuer(self):
        pass

# Dette Model
class Dette(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    dateEcheance = models.DateField()
    montant = models.FloatField()
    statut = models.BooleanField(default=False)

    def __str__(self):
        return f"Dette: {self.id} (Client: {self.client.nom}, Montant: {self.montant})"

    def enregistrer(self):
        if not self.statut :
            self.client.montantImpayee += self.montant
            self.client.save()
            self.save()
        else :
            raise ValueError("Dette déjà enregistrée")

    def payer(self):
        if not self.statut :
            self.client.montantImpayee -= self.montant
            self.client.save()
            self.statut = True
            self.save()
        else :
            raise ValueError("Dette déjà payée")

# Frais Model 
class Frais(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    montant = models.FloatField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Frais: {self.id} (Type: {self.type}, Montant: {self.montant})"

# Notification Model
class Notification(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification: {self.id} (Client: {self.client.nom}, Lu: {self.lu})"

    def envoyer(self):
        pass

    def marquerCommeLu(self):
        pass

# Stock Model (intermediate for Produit/Entrepot)
class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    entrepot = models.ForeignKey(Entrepot, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    seuilAlerte = models.IntegerField()

    def __str__(self):
        return f"Stock: {self.id} (Produit: {self.produit.nom}, Entrepot: {self.entrepot.nom})"

    def verifierNiveauStock(self):
        if self.produit.quantiteDisponible < self.seuilAlerte :
            return True
        else : 
            return False


