import string

import frappe
from frappe import _
from frappe.model.document import Document


class TheatreVenue(Document):
    def validate(self):
        self._validate_layout()
        self.total_capacity = int(self.total_rows) * int(self.seats_per_row)

    def _validate_layout(self):
        if not self.total_rows or int(self.total_rows) <= 0:
            frappe.throw(_("Total Rows must be greater than 0."))

        if not self.seats_per_row or int(self.seats_per_row) <= 0:
            frappe.throw(_("Seats Per Row must be greater than 0."))

        if int(self.total_rows) > len(string.ascii_uppercase):
            frappe.throw(_("Total Rows cannot exceed 26 with the current seat naming scheme."))

    def get_valid_seats(self):
        rows = int(self.total_rows)
        per_row = int(self.seats_per_row)
        seats = []
        for idx in range(rows):
            row = string.ascii_uppercase[idx]
            for seat_idx in range(1, per_row + 1):
                seats.append(f"{row}{seat_idx}")
        return seats
