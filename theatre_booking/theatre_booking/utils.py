import frappe


def ensure_booking_constraints():
    """Create unique constraint to prevent duplicate seat bookings per show."""
    if frappe.db.exists("DocType", "Theatre Booking"):
        frappe.db.add_unique("Theatre Booking", ["show", "seat_number"], "uniq_show_seat_booking")
