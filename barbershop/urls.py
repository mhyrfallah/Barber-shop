from django.urls import path
from . import views

app_name = 'barbershop'

from django.urls import path
from . import views

app_name = "barbershop"

urlpatterns = [
    path("", views.day_select, name="day_list"),
    path("<int:day_id>/slots/", views.slot_list, name="slot_list"),
    path("slot/<int:slot_id>/reserve/", views.reservation_form, name="reserve"),
    path("slot/<int:slot_id>/reserve/submit/", views.reservation_create, name="reservation_create"),
    path("reservation/<int:reservation_id>/done/", views.reservation_done, name="reservation_done"),
]