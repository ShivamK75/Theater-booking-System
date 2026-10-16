import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Show"), "fieldname": "name", "fieldtype": "Link", "options": "Theatre Show", "width": 180},
        {"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 200},
        {"label": _("Venue"), "fieldname": "venue", "fieldtype": "Link", "options": "Theatre Venue", "width": 180},
        {"label": _("Start"), "fieldname": "start_datetime", "fieldtype": "Datetime", "width": 180},
        {"label": _("End"), "fieldname": "end_datetime", "fieldtype": "Datetime", "width": 180},
        {"label": _("Price"), "fieldname": "ticket_price", "fieldtype": "Currency", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    conditions = ["DATE(start_datetime) = %(show_date)s"]
    values = {"show_date": filters.get("show_date") or frappe.utils.today()}

    if filters.get("venue"):
        conditions.append("venue = %(venue)s")
        values["venue"] = filters["venue"]

    if filters.get("title"):
        conditions.append("title LIKE %(title)s")
        values["title"] = f"%{filters['title']}%"

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]

    if filters.get("from_time"):
        conditions.append("TIME(start_datetime) >= %(from_time)s")
        values["from_time"] = filters["from_time"]

    if filters.get("to_time"):
        conditions.append("TIME(start_datetime) <= %(to_time)s")
        values["to_time"] = filters["to_time"]

    return frappe.db.sql(
        f"""
        SELECT name, title, venue, start_datetime, end_datetime, ticket_price, status
        FROM `tabTheatre Show`
        WHERE {' AND '.join(conditions)}
        ORDER BY start_datetime
        """,
        values,
        as_dict=True,
    )
