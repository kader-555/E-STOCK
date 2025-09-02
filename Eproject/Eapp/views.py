from rest_framework import viewsets, status 
from rest_framework.decorators import action 
from rest_framework.response import Response 
from .models import *
from .serializers import *
from .authentication.permission import  *

# Client ViewSet
class ClientViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsClient]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        # bind the authenticated user to the new Client
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def ajouter_au_panier(self, request, pk=None):
        client = self.get_object()
        produit_id = request.data.get('produit_id')
        quantite = int(request.data.get('quantite', 1))
        try:
            produit = Produit.objects.get(id=produit_id)
            ligne_commande = client.ajouterProduitAuPanier(produit, quantite)
            return Response({'status': 'Produit ajouté au panier'})
        except (Produit.DoesNotExist, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def passer_commande(self, request, pk=None):
        client = self.get_object()
        panier = client.panier_set.first()
        try:
            commande = client.passerCommande(panier)
            return Response({'commande_id': commande.id, 'status': 'Commande passée avec succès'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class FournisseurViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    serializer_class = CommandeSerializer

class EntrepotViewSet(viewsets.ModelViewSet):
    queryset = Entrepot.objects.all()
    serializer_class = EntrepotSerializer

    @action(detail=True, methods=['get'])
    def capacite(self, request, pk=None):
        entrepot = self.get_object()
        try:
            pourcentage = entrepot.suivreCapacite
            return Response({'capacite_utilisee': f'{pourcentage}%'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AdminViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

class LigneCommandeViewSet(viewsets.ModelViewSet):
    queryset = LigneCommande.objects.all()
    serializer_class = LigneCommandeSerializer

class PanierViewSet(viewsets.ModelViewSet):
    queryset = Panier.objects.all()
    serializer_class = PanierSerializer

    @action(detail=True, methods=['post'])
    def supprimer_produit(self, request, pk=None):
        panier = self.get_object()
        produit_id = request.data.get('produit_id')
        try:
            produit = Produit.objects.get(pk=produit_id)
            panier.supprimerProduit(produit)
            return Response({'statut': 'Produit supprimé avec succès'})
        except (Produit.DoesNotExist, ValueError) as e:
            return Response({'error': str(e), 'statut': status.HTTP_400_BAD_REQUEST})

    @action(detail=True, methods=['post'])
    def vider(self, request, pk=None):
        panier = self.get_object()
        panier.viderPanier()
        return Response({'statut': 'Panier vidé avec succès !'})

class FactureViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    # permission_classes = [permissions.IsAuthenticated , IsClient]
    queryset = Facture.objects.all()
    serializer_class = FactureSerializer

    @action(detail=True, methods=['post'])
    def generer_pdf(self, request, pk=None):
        facture = self.get_object()
        return facture.genererPDF()

class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer

    @action(detail=True, methods=['post'])
    def effectuer_paiement(self, request, pk=None):
        paiement = self.get_object()
        paiement.effectuer()
        return Response({'statut': 'Paiement effectué avec succès!'})

class DetteViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Dette.objects.all()
    serializer_class = DetteSerializer

    @action(detail=True, methods=['post'])
    def enregistrer_dette(self, request, pk=None):
        dette = self.get_object()
        try:
            dette.enregistrer()
            return Response({'statut': 'Dette enregistrée avec succès!'})
        except ValueError as e:
            return Response({'error': str(e), 'statut': status.HTTP_400_BAD_REQUEST})

    @action(detail=True, methods=['post'])
    def payer_dette(self, request, pk=None):
        dette = self.get_object()
        try:
            dette.payer()
            return Response({'statut': 'Dette payée avec succès!'})
        except ValueError as e:
            return Response({'error': str(e), 'statut': status.HTTP_400_BAD_REQUEST})

class FraisViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Frais.objects.all()
    serializer_class = FraisSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(detail=True, methods=['post'])
    def envoyer_notification(self, request, pk=None):
        notification = self.get_object()
        notification.envoyer()
        return Response({'statut': 'Notification envoyée avec succès!'})

    @action(detail=True, methods=['post'])
    def marquer_comme_lu(self, request, pk=None):
        notification = self.get_object()
        notification.lu = True
        notification.save()
        return Response({'statut': 'Notification marquée comme lue!'})

class StockViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated , IsAdmin]
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    @action(detail=True, methods=['post'])
    def verifier_stock(self, request, pk=None):
        stock = self.get_object()
        try:
            disponible = stock.verifierNiveauStock()
            return Response({'disponible': disponible})
        except (Produit.DoesNotExist, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)