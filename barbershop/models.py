from django.db import models

class Day(models.Model):
    date = models.DateField(unique=True)
    is_available = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {'Open' if self.is_available else 'Closed'}"


class TimeSlot(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='slots')
    start_time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_time']
        unique_together = ('day', 'start_time')

    def __str__(self):
        return f"{self.day.date} {self.start_time} - {'Booked' if self.is_booked else 'Available'}"


class Reservation(models.Model):
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='reservation')
    full_name = models.CharField(max_length=150)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.slot}"