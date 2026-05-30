from django.db import models
from reservations.models import Reservation

class ResultFile(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='result_file')
    file = models.FileField(upload_to='results/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for Reservation {self.reservation.id}"
