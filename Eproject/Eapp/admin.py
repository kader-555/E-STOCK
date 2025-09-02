from django.contrib import admin

# Register your models here.
# filepath: c:\E-STOCK\Eproject\Eapp\admin.py
from django.contrib import admin
from .models import Client, Fournisseur, Produit, Commande, Entrepot, Admin, LigneCommande, Panier, Facture, Paiement, Dette, Frais, Notification, Stock

admin.site.register(Client)
admin.site.register(Fournisseur)
admin.site.register(Produit)
admin.site.register(Commande)
admin.site.register(Entrepot)
admin.site.register(Admin)
admin.site.register(LigneCommande)
admin.site.register(Panier)
admin.site.register(Facture)
admin.site.register(Paiement)
admin.site.register(Dette)
admin.site.register(Frais)
admin.site.register(Notification)
admin.site.register(Stock)