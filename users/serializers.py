from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    pack_type = serializers.CharField(source='profile.pack_type', read_only=True)
    name = serializers.CharField(source='first_name', read_only=True)
    medecinId = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'medecinId', 'pack_type']

    def get_medecinId(self, obj):
        if hasattr(obj, 'medecin_profile'):
            return obj.medecin_profile.id
        return None
