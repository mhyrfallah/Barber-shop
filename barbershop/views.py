import itertools

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static

from .models import Day, Reservation, Service, TimeSlot


def _slot_taken(request, slot):
    """Shared response for 'someone else got this slot first'."""
    messages.error(request, "Sorry, that time was just taken. Please pick another one.")
    return redirect("barbershop:slot_list", day_id=slot.day_id)


def day_select(request):
    """Step 1 — list open days, each tagged with how many slots are free."""
    days = (
        Day.objects.filter(is_available=True)
        .annotate(
            open_slot_count=Count(
                "slots", filter=Q(slots__is_booked=False)
            )
        )
        .order_by("date")
    )

    preview_images = itertools.cycle([
        "img/Beard-Trim.jpg",
        "img/Hair-Cut.jpg",
        "img/Hair-Wash.jpg",
        "img/Facial.jpg",
    ])
    services_preview = [
        {
            "name": service.name,
            "price": service.price,
            "image_url": static(next(preview_images)),
        }
        for service in Service.objects.filter(is_active=True).exclude(name="سشوار")[:4]
    ]

    return render(request, "barbershop/day_list.html", {
        "days": days,
        "services_preview": services_preview,
    })


def slot_list(request, day_id):
    """Step 2 — list every time slot for the chosen day."""
    day = get_object_or_404(Day, pk=day_id, is_available=True)
    slots = day.slots.order_by("start_time")
    return render(request, "barbershop/slot_list.html", {"day": day, "slots": slots})


def service_select(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    if slot.is_booked:
        return _slot_taken(request, slot)

    if request.method == "POST":
        selected_ids = request.POST.getlist("services")
        if not selected_ids:
            return render(request, "barbershop/service_select.html", {
                "slot": slot,
                "services": Service.objects.filter(is_active=True),
                "error": "Please select at least one service.",
            })
        request.session["selected_service_ids"] = selected_ids
        return redirect("barbershop:reservation_form", slot_id=slot.id)

    return render(request, "barbershop/service_select.html", {
        "slot": slot,
        "services": Service.objects.filter(is_active=True),
    })


def reservation_form(request, slot_id):
    """Step 3 — show the confirm form for one open slot."""
    slot = get_object_or_404(TimeSlot, pk=slot_id)
    if slot.is_booked:
        return _slot_taken(request, slot)
    return render(request, "barbershop/reservation.html", {"slot": slot})


def reservation_create(request, slot_id):
    """Handle the POST from the confirm form. The slot row is locked for the
    duration of the transaction, so two people can't book it at once."""
    if request.method != "POST":
        return redirect("barbershop:reservation_form", slot_id=slot_id)

    full_name = request.POST.get("full_name", "").strip()
    if not full_name:
        messages.error(request, "Please enter your name to reserve this time.")
        return redirect("barbershop:reservation_form", slot_id=slot_id)

    reservation = None
    try:
        with transaction.atomic():
            # Blocks any concurrent request for the same slot until we commit.
            slot = get_object_or_404(TimeSlot.objects.select_for_update(), pk=slot_id)

            if not slot.is_booked:
                reservation = Reservation.objects.create(slot=slot, full_name=full_name)
                slot.is_booked = True
                slot.save(update_fields=["is_booked"])
    except IntegrityError:
        # Backstop: the OneToOne on Reservation.slot rejected a duplicate
        # (e.g. is_booked was out of sync with reality).
        reservation = None

    if reservation is None:
        slot = get_object_or_404(TimeSlot, pk=slot_id)
        return _slot_taken(request, slot)

    # TODO: redirect into your deposit payment flow instead, e.g.
    # return redirect("payments:checkout", reservation_id=reservation.id)
    return redirect("barbershop:reservation_done", reservation_id=reservation.id)


def reservation_done(request, reservation_id):
    """Simple confirmation page until the real payment flow is wired in."""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    return render(request, "barbershop/reservation_confirmed.html", {"reservation": reservation})