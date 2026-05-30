from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Reservation, Ordonnance
from .serializers import ReservationSerializer, OrdonnanceSerializer
import random, math

class ReservationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        role = request.query_params.get('role')
        qs = Reservation.objects.all().order_by('-created_at')
        user = request.user
        if role == 'patient':
            # Patient only sees their own reservations
            qs = qs.filter(patient=user)
        elif role == 'medecin':
            # Doctor sees reservations assigned to them that are delivered or in medical processing
            medical_statuses = ['LIVRE_AU_MEDECIN', 'EN_ANALYSE', 'ORDONNANCE_PRETE', 'TERMINE', 'livre', 'analyse']
            qs = qs.filter(medecin__user=user, status__in=medical_statuses)
        elif role == 'livreur':
            # Livreur sees active transport missions and history
            transport_statuses = ['EN_ATTENTE', 'COLLECTE_EN_COURS', 'COLLECTE_TERMINEE', 'EN_TRANSIT', 'LIVRE_AU_MEDECIN', 'attente', 'cours', 'livre']
            qs = qs.filter(status__in=transport_statuses)
        elif role == 'admin':
            pass # Admin sees everything
            
        serializer = ReservationSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Backend Security: Block service_c for junior users
        user = request.user
        if hasattr(user, 'profile'):
            pack = user.profile.pack_type
            service = request.data.get('service')
            if pack == 'junior' and service == 'service_c':
                return Response({'success': False, 'message': 'Service non autorisé pour votre pack'}, status=status.HTTP_403_FORBIDDEN)

        # Clean "null" strings that come from FormData
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        for k, v in data.items():
            if v == 'null': data[k] = None
            
        serializer = ReservationSerializer(data=data)
        def to_int(val):
            if val is None or val == 'null' or val == '': return None
            try: return int(val)
            except: return None

        if serializer.is_valid():
            try:
                vd = serializer.validated_data
                
                # Get patient GPS from profile
                patient_lat, patient_lng = None, None
                try:
                    patient_id = to_int(vd.get('patient_id') or request.data.get('patientId'))
                    from users.models import UserProfile
                    profile = UserProfile.objects.get(user_id=patient_id)
                    patient_lat = profile.latitude
                    patient_lng = profile.longitude
                except Exception:
                    pass
                # Fallback: random Casablanca position
                if not patient_lat:
                    patient_lat = 33.5831 + random.uniform(-0.01, 0.01)
                    patient_lng = -7.6314 + random.uniform(-0.01, 0.01)

                # Get doctor GPS
                doctor_lat, doctor_lng = None, None
                medecin_id = vd.get('medecin_id')
                if medecin_id:
                    try:
                        from users.models import Medecin
                        med = Medecin.objects.get(id=medecin_id)
                        doctor_lat = med.latitude
                        doctor_lng = med.longitude
                    except Exception:
                        pass
                if not doctor_lat:
                    doctor_lat = 33.5891
                    doctor_lng = -7.6032

                # Generate random starting position for delivery person
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0.005, 0.015)
                delivery_lat = patient_lat + dist * math.cos(angle)
                delivery_lng = patient_lng + dist * math.sin(angle)

                patient_id = vd.get('patient_id') or request.data.get('patientId')
                if not patient_id:
                    return Response({'success': False, 'message': 'ID Patient manquant'}, status=status.HTTP_400_BAD_REQUEST)

                # Use serializer.save() to handle field mapping correctly
                res = serializer.save(
                    patient_id=patient_id,
                    medecin_id=to_int(vd.get('medecin_id') or request.data.get('medecinId')),
                    patient_lat=patient_lat,
                    patient_lng=patient_lng,
                    doctor_lat=doctor_lat,
                    doctor_lng=doctor_lng,
                    delivery_lat=delivery_lat,
                    delivery_lng=delivery_lng,
                )

                # Fetch OSRM route in background
                try:
                    from tracking.views import fetch_osrm_route
                    service = vd.get('service', '')
                    if 'a' in service.lower():
                        route = fetch_osrm_route(delivery_lat, delivery_lng, doctor_lat, doctor_lng)
                    else:
                        route = fetch_osrm_route(delivery_lat, delivery_lng, patient_lat, patient_lng)
                    res.route_geometry = route
                    res.save(update_fields=['route_geometry'])
                except Exception as e:
                    print(f"OSRM route fetch failed: {e}")

                return Response({'success': True, 'reservation': {'id': res.id}})
            except Exception as e:
                print(f"ERROR creating reservation: {e}")
                return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"VALIDATION ERRORS: {serializer.errors}")
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class OrdonnanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            patient_id = data.get('patientId')
            medecin_id = data.get('medecinId')
            res_id = data.get('reservationId')
            contenu = data.get('contenu')

            if not contenu:
                return Response({'success': False, 'message': 'Contenu vide'}, status=status.HTTP_400_BAD_REQUEST)

            ord_obj = Ordonnance.objects.create(
                patient_id=patient_id,
                medecin_id=medecin_id,
                reservation_id=res_id,
                contenu=contenu,
                status='ORDONNANCE_DISPONIBLE'
            )
            
            if ord_obj.reservation:
                ord_obj.reservation.status = 'ORDONNANCE_PRETE'
                ord_obj.reservation.save()
                
            return Response({'success': True, 'ordonnance': {'id': ord_obj.id}})
        except Exception as e:
            print(f"ERROR creating ordonnance: {e}")
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PatientOrdonnanceListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, patient_id=None):
        user = request.user
        # If no patient_id provided in URL, use current user
        target_id = patient_id or user.id
        
        # Security: Patients can only see their own records
        if hasattr(user, 'profile') and user.profile.role == 'patient':
            target_id = user.id
            
        qs = Ordonnance.objects.filter(patient_id=target_id).order_by('-date_creation')
        serializer = OrdonnanceSerializer(qs, many=True)
        return Response(serializer.data)

from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404

class ReservationReceiptView(APIView):
    permission_classes = [] # Public access as requested

    def get(self, request, reservation_id):
        order = get_object_or_404(Reservation, id=reservation_id)
        
        if not order.receipt:
            return Response({'error': 'Aucun reçu fourni'}, status=404)
        
        import mimetypes
        content_type, _ = mimetypes.guess_type(order.receipt.name)
        return FileResponse(order.receipt.open(), content_type=content_type or 'application/octet-stream')
