 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
 
class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Custom serializer for token generation"""
    username = serializers.CharField()
    password = serializers.CharField()
    roles = serializers.CharField()

    def validate(self, attrs):
        from django.contrib.auth.models import User
        from django.contrib.auth import authenticate

        username = attrs.get("username")
        password = attrs.get("password")
        roles = attrs.get("roles")
        user = authenticate(username=username, password=password)
        
        if user:
           
            refresh = RefreshToken.for_user(user)
            refresh.payload["admin"] = roles
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        raise serializers.ValidationError("Invalid credentials")
