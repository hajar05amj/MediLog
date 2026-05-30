from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Livreur, Livraison, NotificationLivreur
from django.utils import timezone
from django.db.models import Sum, Count

def courier_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('delivery:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'delivery/login.html', {'form': form})

def courier_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Livreur.objects.create(
                user=user,
                status='disponible',
                vehicule='Scooter (Standard)',
                phone='0000000000',
                cin=f'CIN-{user.id}'
            )
            login(request, user)
            return redirect('delivery:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'delivery/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get or create livreur profile
    livreur, created = Livreur.objects.get_or_create(
        user=request.user,
        defaults={'status': 'disponible', 'vehicule': 'Non spécifié', 'phone': '0000000000', 'cin': f'CIN-{request.user.id}'}
    )
    
    # Stats
    today = timezone.now().date()
    daily_deliveries = Livraison.objects.filter(livreur=livreur, completed_at__date=today, status='termine').count()
    active_deliveries = Livraison.objects.filter(livreur=livreur, status__in=['accepte', 'en_route', 'collecte'])
    pending_deliveries = Livraison.objects.filter(status='en_attente').order_by('-id')[:5]
    
    # Simulated earnings (for UI demo)
    total_earnings = daily_deliveries * 15.0  # 15 MAD per delivery
    
    context = {
        'livreur': livreur,
        'daily_deliveries': daily_deliveries,
        'active_deliveries': active_deliveries,
        'pending_deliveries': pending_deliveries,
        'total_earnings': total_earnings,
        'recent_notifications': NotificationLivreur.objects.filter(livreur=livreur)[:3]
    }
    return render(request, 'delivery/dashboard.html', context)

@login_required
def livraisons_list(request):
    livreur = Livreur.objects.get(user=request.user)
    available_missions = Livraison.objects.filter(status='en_attente')
    my_missions = Livraison.objects.filter(livreur=livreur).exclude(status__in=['termine', 'annule'])
    
    return render(request, 'delivery/livraisons.html', {
        'available_missions': available_missions,
        'my_missions': my_missions,
        'livreur': livreur
    })

@login_required
def livraison_detail(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)
    return render(request, 'delivery/detail_livraison.html', {'livraison': livraison})

@login_required
def accept_mission(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)
    livreur = Livreur.objects.get(user=request.user)
    
    if livraison.status == 'en_attente':
        livraison.livreur = livreur
        livraison.status = 'accepte'
        livraison.save()
        # Add notification or message
    return redirect('delivery:livraisons')

@login_required
def historique(request):
    livreur = Livreur.objects.get(user=request.user)
    past_deliveries = Livraison.objects.filter(livreur=livreur, status='termine').order_by('-completed_at')
    return render(request, 'delivery/historique.html', {'past_deliveries': past_deliveries})

@login_required
def profil(request):
    livreur = Livreur.objects.get(user=request.user)
    return render(request, 'delivery/profil.html', {'livreur': livreur})

@login_required
def notifications(request):
    livreur = Livreur.objects.get(user=request.user)
    notifs = NotificationLivreur.objects.filter(livreur=livreur)
    return render(request, 'delivery/notifications.html', {'notifications': notifs})
