# barbershop/tests.py
from datetime import date, time, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction

from .models import Day, TimeSlot, Reservation


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
        slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), price=25.00
        )
        self.assertEqual(slot.day, self.day)
        self.assertFalse(slot.is_booked)

    def test_slot_str_available(self):
        slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), price=25.00
        )
        self.assertIn("Available", str(slot))

    def test_slot_str_booked(self):
        slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), price=25.00, is_booked=True
        )
        self.assertIn("Booked", str(slot))

    def test_unique_together_day_and_start_time(self):
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0), price=25.00)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TimeSlot.objects.create(day=self.day, start_time=time(9, 0), price=30.00)

    def test_same_start_time_different_day_allowed(self):
        other_day = Day.objects.create(date=date.today() + timedelta(days=1))
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0), price=25.00)
        # Should not raise
        TimeSlot.objects.create(day=other_day, start_time=time(9, 0), price=25.00)
        self.assertEqual(TimeSlot.objects.count(), 2)

    def test_slots_ordered_by_start_time(self):
        TimeSlot.objects.create(day=self.day, start_time=time(11, 0), price=25.00)
        TimeSlot.objects.create(day=self.day, start_time=time(9, 0), price=25.00)
        times = list(TimeSlot.objects.values_list('start_time', flat=True))
        self.assertEqual(times, sorted(times))


class ReservationModelTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date.today(), is_available=True)
        self.slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), price=25.00
        )

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

# barbershop/tests.py  (add these classes below your existing model tests)

from django.urls import reverse
from datetime import date, time, timedelta


class DayListViewTests(TestCase):
    def setUp(self):
        self.available_day = Day.objects.create(date=date.today(), is_available=True)
        self.unavailable_day = Day.objects.create(
            date=date.today() + timedelta(days=1), is_available=False
        )

    def test_status_code_200(self):
        response = self.client.get(reverse('barbershop:day_list'))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse('barbershop:day_list'))
        self.assertTemplateUsed(response, 'barbershop/day_list.html')

    def test_only_available_days_shown(self):
        response = self.client.get(reverse('barbershop:day_list'))
        days_in_context = list(response.context['days'])
        self.assertIn(self.available_day, days_in_context)
        self.assertNotIn(self.unavailable_day, days_in_context)

    def test_empty_state_when_no_available_days(self):
        Day.objects.all().delete()
        response = self.client.get(reverse('barbershop:day_list'))
        self.assertContains(response, "No available days right now.")

    def test_days_ordered_by_date(self):
        Day.objects.all().delete()
        d1 = Day.objects.create(date=date.today() + timedelta(days=2), is_available=True)
        d2 = Day.objects.create(date=date.today(), is_available=True)
        response = self.client.get(reverse('barbershop:day_list'))
        days_in_context = list(response.context['days'])
        self.assertEqual(days_in_context, [d2, d1])


class DayDetailViewTests(TestCase):
    def setUp(self):
        self.day = Day.objects.create(date=date.today(), is_available=True)
        self.unavailable_day = Day.objects.create(
            date=date.today() + timedelta(days=1), is_available=False
        )
        self.open_slot = TimeSlot.objects.create(
            day=self.day, start_time=time(9, 0), price=25.00, is_booked=False
        )
        self.booked_slot = TimeSlot.objects.create(
            day=self.day, start_time=time(10, 0), price=25.00, is_booked=True
        )

    def test_status_code_200_for_available_day(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.day.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.day.id])
        )
        self.assertTemplateUsed(response, 'barbershop/day_detail.html')

    def test_404_for_unavailable_day(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.unavailable_day.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_404_for_nonexistent_day(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[9999])
        )
        self.assertEqual(response.status_code, 404)

    def test_only_unbooked_slots_shown(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.day.id])
        )
        slots_in_context = list(response.context['slots'])
        self.assertIn(self.open_slot, slots_in_context)
        self.assertNotIn(self.booked_slot, slots_in_context)

    def test_empty_state_when_no_open_slots(self):
        self.open_slot.is_booked = True
        self.open_slot.save()
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.day.id])
        )
        self.assertContains(response, "No open slots for this day.")

    def test_context_contains_correct_day(self):
        response = self.client.get(
            reverse('barbershop:day_detail', args=[self.day.id])
        )
        self.assertEqual(response.context['day'], self.day)