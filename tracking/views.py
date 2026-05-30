from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from reservations.models import Reservation
from .models import TrackingLog
import requests, random, math

class UpdateStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, res_id):
        new_status = request.data.get('status')
        prescription_text = request.data.get('prescription')
        try:
            r = Reservation.objects.get(id=res_id)
            r.status = new_status
            if prescription_text:
                r.prescription = prescription_text
            r.save()
            TrackingLog.objects.create(reservation=r, status=new_status)
            return Response({'success': True})
        except Reservation.DoesNotExist:
            return Response({'success': False, 'message': 'Non trouvé'}, status=status.HTTP_404_NOT_FOUND)


class TrackingDataView(APIView):
    """GET /reservations/<id>/tracking/ — Returns positions + route for a reservation"""
    permission_classes = [IsAuthenticated]

    def get(self, request, res_id):
        try:
            res = Reservation.objects.select_related('patient', 'medecin').get(id=res_id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        # Build response with positions
        data = {
            'id': res.id,
            'status': res.status,
            'service': res.service,
            'patient': {
                'lat': res.patient_lat,
                'lng': res.patient_lng,
                'label': f"Domicile {res.patient.username}" if res.patient else "Patient"
            },
            'doctor': {
                'lat': res.doctor_lat,
                'lng': res.doctor_lng,
                'label': f"Dr. {res.medecin.nom}" if res.medecin else "Médecin"
            },
            'delivery': {
                'lat': res.delivery_lat,
                'lng': res.delivery_lng,
                'label': 'Livreur'
            },
            'route': res.route_geometry or [],
            'distance_km': None,
            'eta_minutes': None,
        }

        # Calculate distance and ETA if we have positions
        if res.delivery_lat and res.patient_lat:
            dest_lat = res.patient_lat
            dest_lng = res.patient_lng
            # For service A, destination is doctor
            if res.service and 'a' in res.service.lower():
                dest_lat = res.doctor_lat or res.patient_lat
                dest_lng = res.doctor_lng or res.patient_lng

            if dest_lat and dest_lng:
                dist = haversine(res.delivery_lat, res.delivery_lng, dest_lat, dest_lng)
                data['distance_km'] = round(dist, 2)
                data['eta_minutes'] = max(1, round(dist / 0.5))  # ~30km/h in city

        return Response(data)


class TrackingUpdateView(APIView):
    """POST /reservations/<id>/tracking/update/ — Update delivery position"""
    permission_classes = [IsAuthenticated]

    def post(self, request, res_id):
        lat = request.data.get('lat')
        lng = request.data.get('lng')

        if lat is None or lng is None:
            return Response({'error': 'lat and lng required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            res = Reservation.objects.get(id=res_id)
            res.delivery_lat = float(lat)
            res.delivery_lng = float(lng)
            res.save(update_fields=['delivery_lat', 'delivery_lng'])

            # Also save to TrackingGPS if delivery app is set up
            try:
                from delivery.models import TrackingGPS, Livraison
                livraison = Livraison.objects.filter(reservation=res).first()
                if livraison:
                    TrackingGPS.objects.create(
                        livraison=livraison,
                        latitude=float(lat),
                        longitude=float(lng)
                    )
            except Exception:
                pass  # TrackingGPS is optional

            return Response({'success': True, 'lat': res.delivery_lat, 'lng': res.delivery_lng})
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation non trouvée'}, status=status.HTTP_404_NOT_FOUND)


class InitRouteView(APIView):
    """POST /reservations/<id>/tracking/init-route/ — Generate OSRM route and set initial positions"""
    permission_classes = [IsAuthenticated]

    def post(self, request, res_id):
        try:
            res = Reservation.objects.select_related('patient', 'medecin').get(id=res_id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation non trouvée'}, status=status.HTTP_404_NOT_FOUND)

        # Get patient position from profile
        if not res.patient_lat:
            try:
                profile = res.patient.profile
                res.patient_lat = profile.latitude or 33.5831
                res.patient_lng = profile.longitude or -7.6314
            except Exception:
                res.patient_lat = 33.5831
                res.patient_lng = -7.6314

        # Get doctor position
        if not res.doctor_lat and res.medecin:
            res.doctor_lat = res.medecin.latitude or 33.5891
            res.doctor_lng = res.medecin.longitude or -7.6032

        # Generate realistic starting position for delivery person (nearby random offset)
        if not res.delivery_lat:
            base_lat = res.patient_lat
            base_lng = res.patient_lng
            # Random offset 500m-2km from patient
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.005, 0.015)  # ~0.5-1.5km
            res.delivery_lat = base_lat + dist * math.cos(angle)
            res.delivery_lng = base_lng + dist * math.sin(angle)

        # Determine destination based on service type
        dest_lat, dest_lng = res.patient_lat, res.patient_lng
        if res.service and 'a' in res.service.lower() and res.doctor_lat:
            # Service A: deliver to doctor
            dest_lat, dest_lng = res.doctor_lat, res.doctor_lng

        # Fetch route from OSRM
        route_coords = fetch_osrm_route(
            res.delivery_lat, res.delivery_lng,
            dest_lat, dest_lng
        )
        res.route_geometry = route_coords
        res.save()

        return Response({
            'success': True,
            'patient': {'lat': res.patient_lat, 'lng': res.patient_lng},
            'doctor': {'lat': res.doctor_lat, 'lng': res.doctor_lng},
            'delivery': {'lat': res.delivery_lat, 'lng': res.delivery_lng},
            'route': res.route_geometry,
            'route_points': len(res.route_geometry) if res.route_geometry else 0
        })


def fetch_osrm_route(start_lat, start_lng, end_lat, end_lng):
    """Fetch a real route from OSRM (free, no API key needed)"""
    try:
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{start_lng},{start_lat};{end_lng},{end_lat}"
            f"?overview=full&geometries=geojson"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if data.get('code') == 'Ok' and data.get('routes'):
            coords = data['routes'][0]['geometry']['coordinates']
            # OSRM returns [lng, lat], convert to [lat, lng] for Leaflet
            return [[c[1], c[0]] for c in coords]
    except Exception as e:
        print(f"OSRM Error: {e}")

    # Fallback: generate a simple interpolated path
    steps = 20
    return [
        [
            start_lat + (end_lat - start_lat) * i / steps,
            start_lng + (end_lng - start_lng) * i / steps
        ]
        for i in range(steps + 1)
    ]


def haversine(lat1, lng1, lat2, lng2):
    """Calculate distance in km between two GPS points"""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
