from django.contrib import admin
from .models import Livreur, Livraison, TrackingGPS, NotificationLivreur, MessageChat

@admin.register(Livreur)
class LivreurAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicule', 'status', 'is_online', 'last_updated')
    list_filter = ('status', 'is_online')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'cin')

@admin.register(Livraison)
class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'reservation', 'livreur', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('reservation__patient__username', 'livreur__user__username')

@admin.register(TrackingGPS)
class TrackingGPSAdmin(admin.ModelAdmin):
    list_display = ('livraison', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp',)

@admin.register(NotificationLivreur)
class NotificationLivreurAdmin(admin.ModelAdmin):
    list_display = ('livreur', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')

@admin.register(MessageChat)
class MessageChatAdmin(admin.ModelAdmin):
    list_display = ('livraison', 'sender', 'timestamp')
    list_filter = ('timestamp',)
