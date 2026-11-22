from django.contrib import admin
from .models import Day, TimeSlot, Reservation, Service


@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("date", "is_available")
    list_filter = ("is_available",)
    ordering = ("date",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("day", "start_time", "is_booked")
    list_filter = ("day__date", "is_booked")
    ordering = ("day", "start_time")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "slot", "is_paid", "reminder_sent", "created_at")
    list_filter = ("is_paid", "reminder_sent")
    search_fields = ("full_name", "phone_number")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "create_at")
    list_filter = ("is_active",)
    ordering = ("name",)