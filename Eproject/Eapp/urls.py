from django.urls import path,include
from rest_framework.routers import DefaultRouter # pyright: ignore[reportMissingImports]
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from .authentication import views as auth_view

router = DefaultRouter()
router.register(r'clients',ClientViewSet)
router.register(r'fournisseurs',FournisseurViewSet)
router.register(r'produits',ProduitViewSet)
router.register(r'commandes',CommandeViewSet)
router.register(r'entrepots',EntrepotViewSet)
router.register(r'lignecommandes',LigneCommandeViewSet)
router.register(r'admins',AdminViewSet)
router.register(r'paniers',PanierViewSet)
router.register(r'factures',FactureViewSet)
router.register(r'paiements',PaiementViewSet)
router.register(r'dettes',DetteViewSet)
router.register(r'frais',FraisViewSet)
router.register(r'notifications',NotificationViewSet)
router.register(r'stocks',StockViewSet)
urlpatterns = [
    path('',include(router.urls)),
    path('api-auth/',include('rest_framework.urls',namespace = 'rest_framework')),
    # ----- Authentication Urls -----
    path('auth/login/',auth_view.login_view,name='login'),
    path('auth/logout/',auth_view.logout_view,name = 'logout'),
    path('auth/register/client/',auth_view.client_register,name='client_register'),
    path('auth/register/admin/',auth_view.admin_register,name='admin_register'),
    path('auth/current_user/',auth_view.current_user, name= 'current_user'),
    path('auth/refresh/',TokenRefreshView.as_view(),name='token_refresh'),


]


