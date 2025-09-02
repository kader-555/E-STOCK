from rest_framework import  status ,permissions
from rest_framework.decorators import api_view , permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response 
from django.contrib.auth import login, logout 
from ..models import *
from ..serializers import *

# --------Authentication Views--------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data= request.data)
    if serializer.is_valid() :
        user = serializer.validated_data['user']
        login(request,user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user' : UserSerializer(user).data,
                'refresh': str(refresh),
                'access':str(refresh.access_token)
            },status= status.HTTP_200_OK
        )
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({
            'detail' :'déconnection avec succés'
            },status= status.HTTP_200_OK
        )

# Client register view
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def client_register(request):
    serializer = ClientRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        client = serializer.save()

        # login the user automatically after registration 
        login(request, client.user)

        # JWT token generation 
        refresh = RefreshToken.for_user(client.user)

        return Response({
            'user' : UserSerializer(client.user).data,
            'client' : ClientSerializer(client).data,
            'refresh': str(refresh),
            'access' : str(refresh.access_token)
        },status = status.HTTP_201_CREATED)
    return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)

# Admin register view
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_register(request):
    serializer = AdminRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()

        # login the user automatically after registration 
        login(request, admin.user)

        # JWT token generation 
        refresh = RefreshToken.for_user(admin.user)

        return Response({
            'user': UserSerializer(admin.user).data,
            'admin': AdminSerializer(admin).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Current User
@api_view(['GET'])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

