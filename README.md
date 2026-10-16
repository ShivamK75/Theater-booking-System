# Theatre Booking System (Frappe App)

This repository contains a standalone Frappe app: `theatre_booking`.

## Install on a site that already has ERPNext

```bash
# from your bench apps directory
git clone https://github.com/ShivamK75/Theater-booking-System.git theatre_booking

# from bench root
bench --site <site-name> install-app theatre_booking
bench --site <site-name> migrate
```

## Data model

### 1) Theatre Venue (`Theatre Venue`)
Stores auditorium details and seat layout settings:
- `venue_name`
- `total_rows`
- `seats_per_row`
- `total_capacity` (derived server-side)

Seats are generated server-side as `A1..A<n>, B1..B<n> ...` from rows and seats-per-row.

### 2) Theatre Show (`Theatre Show`)
Stores show scheduling and pricing:
- `title`
- `venue`
- `start_datetime`
- `end_datetime`
- `ticket_price`
- `status` (Scheduled / Completed / Cancelled)

### 3) Theatre Booking (`Theatre Booking`)
Stores seat-level bookings:
- `show`
- `venue` (derived from show)
- `seat_number`
- `amount_due` (derived from show ticket price)
- `booking_status` (Draft / Confirmed / Cancelled)

A DB-level composite unique constraint on `(show, seat_number)` prevents duplicate seat booking for the same show.

## Reused Frappe/ERPNext capabilities

Reused platform capabilities instead of modifying Frappe/ERPNext source:
- Standard DocTypes, Link fields, list views, report framework
- Server-side document validation hooks (`validate`)
- Role/permission model (`System Manager`)
- Naming series/autoname patterns
- Script Report for filtered current-date show visibility

Alternatives considered and rejected:
- Modifying ERPNext item/sales doctypes for seat booking: rejected to keep the app isolated and maintainable.
- Client-only seat checks: rejected because server-side enforcement is required.
- Non-DB duplicate checks only: rejected because race conditions require DB-backed uniqueness.

## Server-side validation decisions

- Required fields are enforced through DocType metadata.
- Show rules:
  - End must be after start.
  - Ticket price must be positive.
  - Overlapping shows in the same venue are blocked.
  - Key fields (`venue`, `start_datetime`, `end_datetime`, `ticket_price`) cannot change after bookings exist.
- Booking rules:
  - Amount due always comes from show ticket price.
  - Seat must be valid for the selected venue layout.
  - Cannot create/update booking for cancelled shows.
  - Booking status transitions are restricted.
  - `show` and `seat_number` are immutable after creation.

## Current-date visibility and filtering

A Script Report **"Today's Shows"** is included with filters:
- Date (defaults to today)
- Venue
- Title (contains)
- Status
- From Time / To Time

## Demonstrating required flows

1. Create a `Theatre Venue` with rows and seats-per-row.
2. Create a `Theatre Show` with venue, start/end, and ticket price.
3. Create a `Theatre Booking` with show + seat (example `A1`).
4. Confirm `amount_due` auto-populates from show ticket price.
5. Attempt a second booking with same show + seat and verify duplicate is blocked.
6. Open report **Today's Shows** and apply filters.

## Tests

Run focused app tests:

```bash
bench --site <site-name> run-tests --app theatre_booking
```

Covered cases:
- show date/time and price validation
- show overlap validation
- booking amount propagation from show price
- duplicate seat prevention
- invalid seat rejection
- current-date report filtering
