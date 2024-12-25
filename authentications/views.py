from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from rest_framework import status
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
# Create your views here.

class demoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({'status': 'ok'})
    
class registerView(APIView):

    def post(self, request):
        username = request.data.get('username') 
        password = request.data.get('password')
        roles = request.data.get('roles')
        if not username or not password:
            return Response({'status': 'Please provide username and password'})
        user = authenticate(username=username ,password=password) 
        if user:
            return Response({'status': 'User already exists'})  
        
        user = User.objects.create_user(username=username, password=password)
        user.save()
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        access_token.payload['roles'] = roles   
        
        response = Response({
                'access': str(access_token),

                'refresh': str(refresh),    
                'username': username

            }, status=status.HTTP_200_OK)
            
        response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,  
                samesite='Strict'  

            )
        return response
           
class loginView(APIView):
    def post(self, request):
        # username = request.data.get('username')
        # password = request.data.get('password')
        # if not username or not password:
        #     return Response({'status': 'Please provide username and password'})
        # user = authenticate(username=username, password=password)
        # if not user:
        #     return Response({'status': 'Invalid credentials'})
        # refresh = RefreshToken.for_user(user)
        # return Response({
        #     'status': 'Login successful',
        #     'access': str(refresh.access_token),
        #     'refresh': str(refresh),
        #     'username': username
        # })
    
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                access_token = refresh.access_token
                return Response({
                    'access': str(access_token),
                    'login': 'auto Login successful'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                
                return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        username = request.data.get('username')
        password = request.data.get('password')
        roles = request.data.get('roles')   
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            access_token.payload['roles'] = roles
            response = Response({
                'access': str(access_token),
            }, status=status.HTTP_200_OK)
            
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=True,  
                samesite='Strict'  
            )
            return response
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer