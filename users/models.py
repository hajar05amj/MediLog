from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('medecin', 'Médecin'),
        ('livreur', 'Livreur'),
        ('admin', 'Administrateur'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    ville = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pack_type = models.CharField(max_length=10, choices=(('junior', 'Junior'), ('senior', 'Senior')), default='junior', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medecin_profile', null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    email = models.EmailField(unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.user:
            # Use email as username for consistency
            username = self.email
            
            password = "medilog_default_password"
            user = User.objects.create_user(username=username, email=self.email, password=password)
            self.user = user
            
            # Create UserProfile
            UserProfile.objects.create(user=user, role='medecin', telephone=self.telephone, specialite=self.specialite)
            
            print(f"DEBUG: Created account for {self.nom}: {username} / {password}")
            # In a real app, send email here
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.nom} {self.prenom}"
