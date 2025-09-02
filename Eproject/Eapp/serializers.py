from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Client, Fournisseur, Produit, Commande, Entrepot, Admin, LigneCommande, Panier, Facture, Paiement, Dette, Frais, Notification, Stock

# -------------Model Serializers-------------
class ClientSerializer(serializers.ModelSerializer):
    class Meta :
        model = Client 
        fields = '__all__'  # keep all fields exposed
        read_only_fields = ['user']  # make user assignment server-side for safety

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta :
        model = Fournisseur 
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    class Meta :
        model = Produit 
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    montant_total = serializers.ReadOnlyField(source='montantTotal')
    class Meta :
        model = Commande 
        fields = '__all__'

class EntrepotSerializer(serializers.ModelSerializer):
    capacite_utilisee = serializers.ReadOnlyField()
    class Meta :
        model = Entrepot 
        fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    class Meta :
        model = Admin 
        fields = '__all__'

class LigneCommandeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LigneCommande
        fields = '__all__'

class PanierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panier
        fields = '__all__'

class FactureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facture
        fields = '__all__'

class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = '__all__'

class DetteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dette
        fields = '__all__'

class FraisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frais
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

# -------------Login Serializer-------------
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta :
        model = CustomUser
        fields = ['id','username','email','first_name','last_name','user_type']
# Login Serializer
class LoginSerializer(serializers.Serializer):
    # initailisation de fields :
    username = serializers.CharField()
    password = serializers.CharField()

    # is_valide methode :
    def validate(self,data):
        username = data.get('username','')
        password = data.get('password','')
        if username and password :
            user = authenticate(username = username , password = password)
            if user :
                if user.is_active :
                    data['user'] = user 
                else : 
                    raise serializers.ValidationError("utilisateur  desactivé !")
            else :
                raise serializers.ValidationError("utilisateur Invalide!")
        else :
            raise serializers.ValidationError("Obligatoire d'entrer motdepass et nom d'utilisateur")
        return data 
# Client Registration Serializer  
class ClientRegistrationSerializer(serializers.ModelSerializer):
    # extra fields pour la confirmation de mot de passe:
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Client
        fields = ('username', 'nom', 'adresse', 'telephone', 'email', 'password', 'password2')
    
    # methode de validation 
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    # methode de creation :
    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        # Creer un nouveau utilisateur:
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.get('nom', '').split(' ')[0],
            last_name=' '.join(validated_data.get('nom', '').split(' ')[1:]),
            user_type=1            
        )

        # creer un nouveau client :
        client = Client.objects.create(
            user=user,
            nom=validated_data['nom'],
            adresse=validated_data['adresse'],
            telephone=validated_data['telephone']
        )
        return client 
# Admin Registration Serializer 
class AdminRegistrationSerializer(serializers.ModelSerializer):
    # extra fields pour la confirmation de mot de passe:
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Admin
        fields = ('username', 'nom', 'telephone', 'email', 'password', 'password2')
    
    # methode de validation 
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    # methode de creation :
    def create(self, validated_data):
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        
        # Creer un nouveau utilisateur:
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=validated_data.get('nom', '').split(' ')[0],
            last_name=' '.join(validated_data.get('nom', '').split(' ')[1:]),
            user_type=2           
        )

        # creer un nouveau admin :
        admin = Admin.objects.create(
            user=user,
            nom=validated_data['nom'],
            telephone=validated_data['telephone']
        )
        return admin 