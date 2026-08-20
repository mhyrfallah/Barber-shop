from django.shortcuts import render, get_object_or_404
from .models import Day, TimeSlot


def day_list(request):
    """Show upcoming days that are open for booking."""
    days = Day.objects.filter(is_available=True).order_by('date')
    return render(request, 'barbershop/day_list.html', {'days': days})


def day_detail(request, day_id):
    """Show available (unbooked) time slots for a specific day."""
    day = get_object_or_404(Day, id=day_id, is_available=True)
    slots = day.slots.filter(is_booked=False).order_by('start_time')
    return render(request, 'barbershop/day_detail.html', {'day': day, 'slots': slots})