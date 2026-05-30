from django.db import models
from reservations.models import Reservation

class TrackingLog(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='tracking_logs')
    status = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log: {self.reservation.id} -> {self.status}"
