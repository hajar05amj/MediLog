from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations_as_patient')
    medecin = models.ForeignKey('users.Medecin', on_delete=models.SET_NULL, null=True, related_name='reservations_as_medecin')
    medecin_name = models.CharField(max_length=255, blank=True)
    service = models.CharField(max_length=100)
    service_name = models.CharField(max_length=255, blank=True)
    date = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    pickup_address = models.TextField(blank=True)
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    contact_proche = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, default='EN_ATTENTE')
    prescription = models.TextField(blank=True, null=True)
    
    # GPS Tracking — positions copiées à la création
    patient_lat = models.FloatField(null=True, blank=True)
    patient_lng = models.FloatField(null=True, blank=True)
    doctor_lat = models.FloatField(null=True, blank=True)
    doctor_lng = models.FloatField(null=True, blank=True)
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    route_geometry = models.JSONField(null=True, blank=True)  # OSRM route points
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation {self.id} - {self.service_name}"

class Ordonnance(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.SET_NULL, related_name='ordonnance_doc', null=True, blank=True)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ordonnances')
    medecin = models.ForeignKey('users.Medecin', on_delete=models.SET_NULL, null=True, related_name='ordonnances_emises')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='ORDONNANCE_DISPONIBLE')

    def __str__(self):
        return f"Ordonnance #{self.id} for Patient {self.patient.id}"
