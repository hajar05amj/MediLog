from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import Medecin
from .models import Reservation, Ordonnance

class ReservationSerializer(serializers.ModelSerializer):
    patientId = serializers.IntegerField(source='patient_id')
    patientName = serializers.CharField(source='patient.username', read_only=True)
    medecinId = serializers.IntegerField(source='medecin_id', required=False, allow_null=True)
    medecinName = serializers.CharField(source='medecin_name', required=False, allow_blank=True)
    serviceName = serializers.CharField(source='service_name', required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    fileUrl = serializers.SerializerMethodField()

    status = serializers.CharField(required=False, default='attente')
    prescription = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    pickupAddress = serializers.CharField(source='pickup_address', required=False, allow_blank=True)
    deliveryAddress = serializers.CharField(source='delivery_address', required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    contactProche = serializers.CharField(source='contact_proche', required=False, allow_blank=True)

    receiptUrl = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'patientId', 'patientName', 'medecinId', 'medecinName', 'service', 
            'service_name', 'serviceName', 'date', 'time', 'pickupAddress', 'deliveryAddress', 
            'notes', 'contactProche', 'status', 'prescription', 'createdAt', 'fileUrl', 'receiptUrl', 'receipt',
            'patient_lat', 'patient_lng', 'doctor_lat', 'doctor_lng',
            'delivery_lat', 'delivery_lng', 'route_geometry'
        ]

    def get_receiptUrl(self, obj):
        if obj.receipt:
            return obj.receipt.url
        return None

    def get_fileUrl(self, obj):
        if obj.status == 'resultat' and hasattr(obj, 'result_file'):
            return obj.result_file.file.url
        return None

class OrdonnanceSerializer(serializers.ModelSerializer):
    patientId = serializers.IntegerField(source='patient_id', required=True)
    medecinId = serializers.IntegerField(source='medecin_id', required=False, allow_null=True)
    reservationId = serializers.IntegerField(source='reservation_id', required=False, allow_null=True)
    serviceName = serializers.CharField(source='reservation.service_name', read_only=True)
    medecinName = serializers.SerializerMethodField()
    comment = serializers.CharField(source='contenu', read_only=True)
    dateCreation = serializers.DateTimeField(source='date_creation', read_only=True)

    results = serializers.SerializerMethodField()

    class Meta:
        model = Ordonnance
        fields = ['id', 'reservationId', 'patientId', 'medecinId', 'medecinName', 'contenu', 'comment', 'results', 'status', 'dateCreation', 'serviceName']

    def get_results(self, obj):
        # Restore mock deterministic results based on reservation ID to match doctor dashboard
        import math
        seed = obj.reservation_id or obj.id
        analyses_config = [
            ('Glycémie à jeun', 'g/L', 0.70, 1.10),
            ('Cholestérol Total', 'g/L', 1.50, 2.00),
            ('Tension Artérielle', '', 10, 14)
        ]
        results = []
        for i, (name, unit, min_v, max_v) in enumerate(analyses_config):
            val_seed = math.sin(seed + i) * 10000
            is_anomalous = (abs(val_seed) % 10) > 7
            value = (max_v * 1.15 if val_seed > 0 else min_v * 0.85) if is_anomalous else (min_v + (abs(val_seed) % (max_v - min_v)))
            
            if name == 'Tension Artérielle':
                systolic = round(value)
                diastolic = round(value * 0.65)
                val_str, status = f"{systolic}/{diastolic}", ("Normale" if 11 <= systolic <= 13 else ("Élevée" if systolic > 13 else "Faible"))
            else:
                val_str, status = f"{value:.2f} {unit}".strip(), ("Normale" if min_v <= value <= max_v else ("Élevée" if value > max_v else "Faible"))
            
            results.append({'name': name, 'value': val_str, 'status': status})
        return results

    def get_medecinName(self, obj):
        if obj.medecin:
            return f"Dr. {obj.medecin.prenom} {obj.medecin.nom}"
        return "Médecin"
