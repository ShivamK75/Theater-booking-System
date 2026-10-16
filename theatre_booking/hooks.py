app_name = "theatre_booking"
app_title = "Theatre Booking"
app_publisher = "Shivam"
app_description = "Standalone Theatre Ticket Booking System"
app_email = ""
app_license = "MIT"

after_migrate = ["theatre_booking.theatre_booking.utils.ensure_booking_constraints"]

# Required for test discovery and module sync
fixtures = []
