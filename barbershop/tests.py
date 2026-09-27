# barbershop/tests.py
from datetime import date, time, timedelta

from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Day, Reservation, TimeSlot, Service


class DayModelTests(TestCase):
    def test_str_representation_open(self):
        day = Day.objects.create(date=date.today(), is_available=True)
        self.assertIn("Open", str(day))

    def test_str_representation_closed(self):
        day = Day.objects.create(date=date.today(), is_available=False)
        self.assertIn("Closed", str(day))

    def test_date_must_be_unique(self):
        Day.objects.create(date=date.today())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Day.objects.create(date=date.today())

    def test_default_is_available_false(self):
        day = Day.objects.create(date=date.today())
        self.assertFalse(day.is_available)


class TimeSlotModelTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date.today(), is_available=True)

    def test_create_slot(self):
        slot = TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        self.assertEqual(slot.day, self.day)
        self.assertFalse(slot.is_booked)

    def test_slot_str_available(self):
        slot = TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        self.assertIn("Available", str(slot))

    def test_slot_str_booked(self):
        slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), is_booked=True
        )
        self.assertIn("Booked", str(slot))

    def test_unique_together_day_and_start_time(self):
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimeSlot.objects.create(day=self.day, start_time=time(9, 0))

    def test_same_start_time_different_day_allowed(self):
        other_day = Day.objects.create(date=date.today() + timedelta(days=1))
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        TimeSlot.objects.create(day=other_day, start_time=time(9, 0))
        self.assertEqual(TimeSlot.objects.count(), 2)

    def test_slots_ordered_by_start_time(self):
        TimeSlot.objects.create(day=self.day, start_time=time(11, 0))
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        times = list(TimeSlot.objects.values_list("start_time", flat=True))
        self.assertEqual(times, sorted(times))


class ReservationModelTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date.today(), is_available=True)
        self.slot = TimeSlot.objects.create(day=self.day, start_time=time(9, 0))

    def test_create_reservation(self):
        res = Reservation.objects.create(slot=self.slot, full_name="John Doe")
        self.assertEqual(res.slot, self.slot)
        self.assertFalse(res.is_paid)
        self.assertIsNotNone(res.created_at)

    def test_reservation_str(self):
        res = Reservation.objects.create(slot=self.slot, full_name="John Doe")
        self.assertIn("John Doe", str(res))

    def test_slot_can_only_have_one_reservation(self):
        Reservation.objects.create(slot=self.slot, full_name="John Doe")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reservation.objects.create(slot=self.slot, full_name="Jane Doe")

    def test_reverse_accessor_from_slot(self):
        res = Reservation.objects.create(slot=self.slot, full_name="John Doe")
        self.assertEqual(self.slot.reservation, res)


class DayListViewTests(TestCase):
    def setUp(self):
        self.available_day = Day.objects.create(date=date.today(), is_available=True)
        self.unavailable_day = Day.objects.create(
            date=date.today() + timedelta(days=1), is_available=False
        )

    def test_status_code_200(self):
        response = self.client.get(reverse("barbershop:day_list"))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse("barbershop:day_list"))
        self.assertTemplateUsed(response, "barbershop/day_list.html")

    def test_only_available_days_shown(self):
        response = self.client.get(reverse("barbershop:day_list"))
        days_in_context = list(response.context["days"])
        self.assertIn(self.available_day, days_in_context)
        self.assertNotIn(self.unavailable_day, days_in_context)

    def test_empty_state_when_no_available_days(self):
        Day.objects.all().delete()
        response = self.client.get(reverse("barbershop:day_list"))
        self.assertContains(response, "No days open right now")

    def test_days_ordered_by_date(self):
        Day.objects.all().delete()
        d1 = Day.objects.create(date=date.today() + timedelta(days=2), is_available=True)
        d2 = Day.objects.create(date=date.today(), is_available=True)
        response = self.client.get(reverse("barbershop:day_list"))
        self.assertEqual(list(response.context["days"]), [d2, d1])


class SlotListViewTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date.today(), is_available=True)
        self.unavailable_day = Day.objects.create(
            date=date.today() + timedelta(days=1), is_available=False
        )
        self.open_slot = TimeSlot.objects.create(day=self.day, start_time=time(9, 0))
        self.booked_slot = TimeSlot.objects.create(
            day=self.day, start_time=time(10, 0), is_booked=True
        )
        self.url = reverse("barbershop:slot_list", args=[self.day.id])

    def test_status_code_200_for_available_day(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_correct_template_used(self):
        self.assertTemplateUsed(self.client.get(self.url), "barbershop/slot_list.html")

    def test_404_for_unavailable_day(self):
        url = reverse("barbershop:slot_list", args=[self.unavailable_day.id])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_404_for_nonexistent_day(self):
        url = reverse("barbershop:slot_list", args=[9999])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_all_slots_listed_in_time_order(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["slots"]), [self.open_slot, self.booked_slot]
        )

    def test_only_open_slot_is_bookable(self):
        response = self.client.get(self.url)
        open_link = reverse("barbershop:service_select", args=[self.open_slot.id])
        booked_link = reverse("barbershop:service_select", args=[self.booked_slot.id])
        self.assertContains(response, open_link)
        self.assertNotContains(response, booked_link)
        self.assertContains(response, "is-booked", count=1)

    def test_empty_state_when_day_has_no_slots(self):
        empty_day = Day.objects.create(
            date=date.today() + timedelta(days=2), is_available=True
        )
        response = self.client.get(reverse("barbershop:slot_list", args=[empty_day.id]))
        self.assertContains(response, "No slots open for this day yet.")

    def test_context_contains_correct_day(self):
        self.assertEqual(self.client.get(self.url).context["day"], self.day)


class DoubleBookingTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date(2026, 10, 1), is_available=True)
        self.slot = TimeSlot.objects.create(day=self.day, start_time=time(10, 0))
        self.cut = Service.objects.create(name="Haircut", price=Decimal("50000"), is_active=True)
        self.beard = Service.objects.create(name="Beard", price=Decimal("30000"), is_active=True)
        self.url = reverse("barbershop:reservation_create", args=[self.slot.id])
        self.slot_list_url = reverse("barbershop:slot_list", args=[self.day.id])

    def client_with(self, *services):
        client = Client()
        session = client.session
        session["selected_service_ids"] = [s.pk for s in services]
        session.save()
        return client

    def test_first_booking_succeeds(self):
        resp = self.client_with(self.cut).post(self.url, {"full_name": "Alex"})
        self.assertEqual(resp.status_code, 302)
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_deposit_is_sum_of_selected_services(self):
        self.client_with(self.cut, self.beard).post(self.url, {"full_name": "Alex"})
        res = Reservation.objects.get()
        self.assertEqual(res.deposit_amount, Decimal("80000"))
        self.assertCountEqual(res.services.all(), [self.cut, self.beard])

    def test_second_booking_is_rejected(self):
        self.client_with(self.cut).post(self.url, {"full_name": "Alex"})
        resp = self.client_with(self.cut).post(self.url, {"full_name": "Sam"})
        self.assertRedirects(resp, self.slot_list_url)
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(Reservation.objects.get().full_name, "Alex")

    def test_integrity_error_is_handled_when_flag_out_of_sync(self):
        Reservation.objects.create(slot=self.slot, full_name="Alex")
        resp = self.client_with(self.cut).post(self.url, {"full_name": "Sam"})
        self.assertRedirects(resp, self.slot_list_url)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_no_services_in_session_redirects_to_service_select(self):
        resp = self.client.post(self.url, {"full_name": "Alex"})
        self.assertRedirects(
            resp, reverse("barbershop:service_select", args=[self.slot.id])
        )
        self.assertEqual(Reservation.objects.count(), 0)

    def test_booked_slot_pages_redirect_instead_of_404(self):
        self.slot.is_booked = True
        self.slot.save()
        for name in ("reservation_form", "service_select"):
            resp = self.client.get(reverse(f"barbershop:{name}", args=[self.slot.id]))
            self.assertRedirects(resp, self.slot_list_url)