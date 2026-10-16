import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime, today


class TestTheatreBooking(FrappeTestCase):
    def setUp(self):
        venue_name = "Main Hall"
        if frappe.db.exists("Theatre Venue", venue_name):
            self.venue = frappe.get_doc("Theatre Venue", venue_name)
        else:
            self.venue = frappe.get_doc(
                {
                    "doctype": "Theatre Venue",
                    "venue_name": venue_name,
                    "total_rows": 5,
                    "seats_per_row": 5,
                }
            ).insert()

    def _new_show(self, **overrides):
        show_count = frappe.db.count("Theatre Show") + 1
        start = add_to_date(now_datetime(), hours=(show_count * 3))
        end = add_to_date(start, hours=2)
        data = {
            "doctype": "Theatre Show",
            "title": f"Hamlet-{show_count}",
            "venue": self.venue.name,
            "start_datetime": start,
            "end_datetime": end,
            "ticket_price": 250,
            "status": "Scheduled",
        }
        data.update(overrides)
        return frappe.get_doc(data).insert()

    def test_show_date_and_price_validation(self):
        start = add_to_date(now_datetime(), hours=2)
        with self.assertRaises(frappe.ValidationError):
            self._new_show(end_datetime=start, start_datetime=add_to_date(start, hours=1))

        with self.assertRaises(frappe.ValidationError):
            self._new_show(ticket_price=0)

    def test_show_overlap_prevention(self):
        first = self._new_show()
        with self.assertRaises(frappe.ValidationError):
            self._new_show(
                title="Overlap",
                start_datetime=add_to_date(first.start_datetime, minutes=30),
                end_datetime=add_to_date(first.end_datetime, minutes=30),
            )

    def test_booking_amount_and_duplicate_seat(self):
        show = self._new_show(title="Booking Show")
        booking = frappe.get_doc(
            {
                "doctype": "Theatre Booking",
                "show": show.name,
                "seat_number": "A1",
                "booking_status": "Confirmed",
            }
        ).insert()

        self.assertEqual(booking.amount_due, show.ticket_price)

        with self.assertRaises((frappe.ValidationError, frappe.UniqueValidationError, frappe.DuplicateEntryError)):
            frappe.get_doc(
                {
                    "doctype": "Theatre Booking",
                    "show": show.name,
                    "seat_number": "A1",
                    "booking_status": "Confirmed",
                }
            ).insert()

    def test_invalid_seat_rejected(self):
        show = self._new_show(title="Seat Validation")
        with self.assertRaises(frappe.ValidationError):
            frappe.get_doc(
                {
                    "doctype": "Theatre Booking",
                    "show": show.name,
                    "seat_number": "Z99",
                    "booking_status": "Confirmed",
                }
            ).insert()

    def test_today_report_filters(self):
        from theatre_booking.theatre_booking.report.todays_shows.todays_shows import get_data

        show = self._new_show(title="Today Filter")
        rows = get_data({"show_date": today(), "venue": self.venue.name, "title": "Today"})
        names = [r["name"] for r in rows]
        self.assertIn(show.name, names)
