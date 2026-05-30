from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile, Medecin
from .serializers import UserSerializer

class LoginView(APIView):
    def post(self, request):
        login_id = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        
        # Try to find user by username or email
        user_obj = User.objects.filter(models.Q(username=login_id) | models.Q(email=login_id)).first()
        
        if user_obj:
            user = authenticate(username=user_obj.username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'success': True, 'user': UserSerializer(user).data, 'token': token.key})
        
        return Response({'success': False, 'message': 'Identifiants incorrects'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create_user(
                username=data.get('email'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('nom', '')
            )
            UserProfile.objects.create(
                user=user, 
                role=data.get('role'),
                pack_type=data.get('pack', 'junior')
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'success': True, 'user': UserSerializer(user).data, 'token': token.key})
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReferenceView(APIView):
    def get(self, request):
        doctors_qs = Medecin.objects.all()
        doctors = [{"id": d.id, "name": f"Dr. {d.nom} {d.prenom}", "specialty": d.specialite} for d in doctors_qs]
        services = [
            {"id": "service_a", "name": "Dépôt chez le médecin"},
            {"id": "service_b", "name": "Livraison à domicile"},
            {"id": "service_c", "name": "Accompagnement"}
        ]
        return Response({"doctors": doctors, "services": services})

class SeedView(APIView):
    def get(self, request):
        print("DEBUG SEED: Starting database reset...")
        from reservations.models import Reservation
        User.objects.all().delete()
        Reservation.objects.all().delete()
        
        u1 = User.objects.create_user(username='patient', email='patient@medilog.com', first_name='M. Ahmed (Patient)')
        u1.set_password('123')
        u1.save()
        UserProfile.objects.create(user=u1, role='patient', pack_type='junior')
        
        u2 = User.objects.create_user(username='medecin', email='medecin@medilog.com', first_name='Dr. Bennani (Médecin)')
        u2.set_password('123')
        u2.save()
        UserProfile.objects.create(user=u2, role='medecin')
        
        u3 = User.objects.create_user(username='livreur', email='livreur@medilog.com', first_name='Karim (Coursier)')
        u3.set_password('123')
        u3.save()
        UserProfile.objects.create(user=u3, role='livreur')

        u_hajar = User.objects.create_user(username='hajar.amajoud@gmail.com', email='hajar.amajoud@gmail.com', first_name='Hajar Amajoud')
        u_hajar.set_password('123')
        u_hajar.save()
        UserProfile.objects.create(user=u_hajar, role='patient', pack_type='senior')
        
        u_hanane = User.objects.create_user(username='hanane@gmail.com', email='hanane@gmail.com', first_name='hanane', last_name='wassid')
        u_hanane.set_password('123')
        u_hanane.save()
        UserProfile.objects.create(user=u_hanane, role='patient', pack_type='junior')

        u_chaimaa = User.objects.create_user(username='najdi@gmail.com', email='najdi@gmail.com', first_name='chaimaa', last_name='Najdi')
        u_chaimaa.set_password('123')
        u_chaimaa.save()
        UserProfile.objects.create(user=u_chaimaa, role='patient', pack_type='junior')

        u_ana = User.objects.create_user(username='ana@gmail.com', email='ana@gmail.com', first_name='ana', last_name='ana')
        u_ana.set_password('123')
        u_ana.save()
        UserProfile.objects.create(user=u_ana, role='patient', pack_type='junior')
        
        Token.objects.get_or_create(user=u1)
        Token.objects.get_or_create(user=u2)
        Token.objects.get_or_create(user=u3)
        
        u4 = User.objects.create_user(username='admin', email='admin@medilog.com', first_name='Super', last_name='Admin')
        u4.set_password('123')
        u4.save()
        UserProfile.objects.create(user=u4, role='admin')
        Token.objects.get_or_create(user=u4)
        
        # Add Doctors from screenshot
        doctors_data = [
            {'nom': 'Dr. Ahmed El Mansouri', 'email': 'ahmed.mansouri@gmail.com', 'tel': '0612345678', 'adr': 'Casablanca - Maarif', 'spec': 'Médecin Généraliste'},
            {'nom': 'Dr. Fatima Zahra Bennani', 'email': 'fatima.bennani@gmail.com', 'tel': '0623456789', 'adr': 'Casablanca - Anfa', 'spec': 'Pédiatre'},
            {'nom': 'Dr. Youssef Alaoui', 'email': 'youssef.alaoui@gmail.com', 'tel': '0634567890', 'adr': 'Casablanca - Gauthier', 'spec': 'Cardiologue'},
            {'nom': 'Dr. Khadija El Fassi', 'email': 'khadija.fassi@gmail.com', 'tel': '0645678901', 'adr': 'Casablanca - Sidi Maarouf', 'spec': 'Dermatologue'},
            {'nom': 'Dr. Omar Berrada', 'email': 'omar.berrada@gmail.com', 'tel': '0656789012', 'adr': 'Casablanca - Ain Diab', 'spec': 'Ophtalmologue'},
        ]
        
        for d in doctors_data:
            # Create Medecin object which auto-creates User and Profile
            parts = d['nom'].replace('Dr. ', '').split(' ', 1)
            nom = parts[1] if len(parts) > 1 else parts[0]
            prenom = parts[0]
            
            med = Medecin.objects.create(
                nom=nom,
                prenom=prenom,
                email=d['email'],
                telephone=d['tel'],
                adresse=d['adr'],
                specialite=d['spec']
            )
            # Override password to '123' for demo
            med.user.set_password('123')
            med.user.save()
            Token.objects.get_or_create(user=med.user)
        from reservations.models import Reservation
        # Add missions for u_hajar (the main user hajar.amajoud@gmail.com)
        for i in range(1, 6):
            Reservation.objects.create(
                patient=u_hajar,
                medecin=Medecin.objects.first(),
                service='service_a' if i%2==0 else 'service_b',
                service_name='Dépôt chez le médecin' if i%2==0 else 'Résultats à domicile',
                date='08-05-2026',
                time=f'1{i}:00',
                pickup_address='Laboratoire Central' if i%2==0 else 'Laboratoire Anfa',
                delivery_address='Residence Al Jawhara',
                status='EN_ATTENTE' if i==1 else ('COLLECTE_TERMINEE' if i==2 else ('LIVRE_AU_MEDECIN' if i==3 else 'TERMINE'))
            )
        
        return Response({'success': True, 'message': 'Base de données réinitialisée avec succès !'})

class AdminStatsView(APIView):
    # permission_classes = [IsAuthenticated] # Disable for demo if needed
    def get(self, request):
        from reservations.models import Reservation
        from django.utils import timezone
        today = timezone.now().date()
        
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        
        total_orders = Reservation.objects.count()
        active_orders = Reservation.objects.exclude(status__in=['TERMINE', 'ANNULE']).count()
        
        # Mock revenue for demo
        revenue = total_orders * 45 
        
        # Stats by service
        stats_service = {
            'A': Reservation.objects.filter(service='service_a').count(),
            'B': Reservation.objects.filter(service='service_b').count(),
            'C': Reservation.objects.filter(service='service_c').count(),
        }
        
        return Response({
            'totalUsers': total_users,
            'newUsersToday': new_users_today,
            'totalOrders': total_orders,
            'activeOrders': active_orders,
            'revenue': revenue,
            'statsService': stats_service
        })

class AdminUserListView(APIView):
    def get(self, request):
        role = request.query_params.get('role')
        qs = User.objects.all().select_related('profile').order_by('-date_joined')
        if role:
            qs = qs.filter(profile__role=role)
            
        data = []
        for u in qs:
            data.append({
                'id': u.id,
                'name': f"{u.first_name} {u.last_name}".strip() or u.username,
                'email': u.email,
                'role': u.profile.role if hasattr(u, 'profile') else 'N/A',
                'telephone': u.profile.telephone if hasattr(u, 'profile') else '',
                'adresse': u.profile.adresse if hasattr(u, 'profile') else '',
                'specialite': u.profile.specialite if hasattr(u, 'profile') else '',
                'dateJoined': u.date_joined.strftime('%Y-%m-%d'),
                'status': 'Actif' if u.is_active else 'Inactif'
            })
        return Response(data)

class AdminUserDetailView(APIView):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
        
    def put(self, request, pk):
        user = User.objects.get(pk=pk)
        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.email = data.get('email', user.email)
        user.save()
        
        profile = user.profile
        profile.telephone = data.get('telephone', profile.telephone)
        profile.adresse = data.get('adresse', profile.adresse)
        profile.specialite = data.get('specialite', profile.specialite)
        profile.save()
        
        return Response({'success': True})
        
    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'success': True})

class AdminActivityView(APIView):
    def get(self, request):
        from reservations.models import Reservation
        # We take the 10 most recent reservations as "activity"
        recent = Reservation.objects.all().order_by('-created_at')[:10]
        logs = []
        for r in recent:
            patient_name = r.patient.first_name if r.patient else "Utilisateur"
            logs.append({
                'id': r.id,
                'type': 'ORDER',
                'title': f"Nouvelle mission: {r.service_name}",
                'user': patient_name,
                'time': r.created_at.strftime('%H:%M'),
                'status': r.status
            })
        return Response(logs)
