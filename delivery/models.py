from django.db import models
from django.contrib.auth.models import User
from reservations.models import Reservation

class Livreur(models.Model):
    STATUS_CHOICES = (
        ('disponible', 'Disponible'),
        ('occupe', 'Occupé'),
        ('hors_ligne', 'Hors-ligne'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='livreur_profile')
    phone = models.CharField(max_length=20)
    cin = models.CharField(max_length=20, unique=True)
    vehicule = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='livreurs/', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='hors_ligne')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Livreur: {self.user.get_full_name()} ({self.vehicule})"

class Livraison(models.Model):
    STATUS_LIVRAISON = (
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('en_route', 'En route'),
        ('collecte', 'Colis récupéré'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    )
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='livraison')
    livreur = models.ForeignKey(Livreur, on_delete=models.SET_NULL, null=True, blank=True, related_name='livraisons')
    status = models.CharField(max_length=20, choices=STATUS_LIVRAISON, default='en_attente')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    proof_of_delivery = models.ImageField(upload_to='proofs/', null=True, blank=True)
    signature = models.TextField(null=True, blank=True) # Base64 signature
    qr_code_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Livraison #{self.id} - {self.status}"

class TrackingGPS(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class NotificationLivreur(models.Model):
    livreur = models.ForeignKey(Livreur, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class MessageChat(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
