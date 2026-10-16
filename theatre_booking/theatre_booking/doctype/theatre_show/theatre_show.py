import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime


class TheatreShow(Document):
    def validate(self):
        self._validate_times()
        self._validate_price()
        self._validate_overlap()
        self._validate_key_field_change_after_bookings()

    def _validate_times(self):
        if not self.start_datetime or not self.end_datetime:
            frappe.throw(_("Start and End Date-Time are required."))

        if get_datetime(self.end_datetime) <= get_datetime(self.start_datetime):
            frappe.throw(_("End Date-Time must be after Start Date-Time."))

    def _validate_price(self):
        if not self.ticket_price or float(self.ticket_price) <= 0:
            frappe.throw(_("Ticket Price must be greater than 0."))

    def _validate_overlap(self):
        if not self.venue or not self.start_datetime or not self.end_datetime:
            return

        overlap = frappe.db.sql(
            """
            SELECT name
            FROM `tabTheatre Show`
            WHERE venue = %(venue)s
              AND status != 'Cancelled'
              AND name != %(name)s
              AND start_datetime < %(end_datetime)s
              AND end_datetime > %(start_datetime)s
            LIMIT 1
            """,
            {
                "venue": self.venue,
                "name": self.name or "",
                "start_datetime": self.start_datetime,
                "end_datetime": self.end_datetime,
            },
        )
        if overlap:
            frappe.throw(
                _("Show overlaps with existing show {0} in venue {1}.").format(
                    frappe.bold(overlap[0][0]), frappe.bold(self.venue)
                )
            )

    def _validate_key_field_change_after_bookings(self):
        if self.is_new():
            return

        if not frappe.db.exists("Theatre Booking", {"show": self.name}):
            return

        previous = self.get_doc_before_save()
        if not previous:
            return

        key_fields = ["venue", "start_datetime", "end_datetime", "ticket_price"]
        changed = [f for f in key_fields if previous.get(f) != self.get(f)]
        if changed:
            frappe.throw(
                _("Cannot change {0} after bookings exist for this show.").format(
                    ", ".join(changed)
                )
            )
