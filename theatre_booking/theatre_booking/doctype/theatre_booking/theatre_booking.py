import frappe
from frappe import _
from frappe.model.document import Document


class TheatreBooking(Document):
    def validate(self):
        self._validate_show_status()
        self._validate_key_field_immutability()
        self._set_amount_due_from_show()
        self._validate_seat()
        self._validate_duplicate_booking()
        self._validate_booking_status_transition()

    def _validate_show_status(self):
        show_status = frappe.db.get_value("Theatre Show", self.show, "status")
        if show_status == "Cancelled":
            frappe.throw(_("Cannot create or update booking against a cancelled show."))

    def _set_amount_due_from_show(self):
        ticket_price, venue = frappe.db.get_value(
            "Theatre Show", self.show, ["ticket_price", "venue"]
        )
        if not ticket_price:
            frappe.throw(_("Ticket price is not set for selected show."))

        self.amount_due = ticket_price
        self.venue = venue

    def _validate_seat(self):
        self.seat_number = (self.seat_number or "").strip().upper()
        venue_doc = frappe.get_doc("Theatre Venue", self.venue)
        valid_seats = set(venue_doc.get_valid_seats())
        if self.seat_number not in valid_seats:
            frappe.throw(
                _("Seat {0} is not valid for venue {1}.").format(
                    frappe.bold(self.seat_number), frappe.bold(self.venue)
                )
            )

    def _validate_duplicate_booking(self):
        if not self.show or not self.seat_number:
            return

        duplicate = frappe.db.exists(
            "Theatre Booking",
            {"show": self.show, "seat_number": self.seat_number, "name": ["!=", self.name]},
        )
        if duplicate:
            frappe.throw(
                _("Seat {0} is already booked for show {1}.").format(
                    frappe.bold(self.seat_number), frappe.bold(self.show)
                )
            )

    def _validate_booking_status_transition(self):
        allowed = {
            "Draft": {"Draft", "Confirmed", "Cancelled"},
            "Confirmed": {"Confirmed", "Cancelled"},
            "Cancelled": {"Cancelled"},
        }

        if self.is_new():
            if self.booking_status not in allowed["Draft"]:
                frappe.throw(_("Invalid initial booking status."))
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        from_status = previous.booking_status or "Draft"
        to_status = self.booking_status or "Draft"
        if to_status not in allowed.get(from_status, set()):
            frappe.throw(
                _("Invalid booking status transition from {0} to {1}.").format(
                    from_status, to_status
                )
            )

    def _validate_key_field_immutability(self):
        if self.is_new():
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        for field in ("show", "seat_number"):
            if previous.get(field) != self.get(field):
                frappe.throw(_("Field {0} cannot be changed after booking creation.").format(field))
