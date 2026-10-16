frappe.query_reports["Today's Shows"] = {
  filters: [
    {
      fieldname: "show_date",
      label: "Date",
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      reqd: 1,
    },
    {
      fieldname: "venue",
      label: "Venue",
      fieldtype: "Link",
      options: "Theatre Venue",
    },
    {
      fieldname: "title",
      label: "Title",
      fieldtype: "Data",
    },
    {
      fieldname: "status",
      label: "Status",
      fieldtype: "Select",
      options: "\nScheduled\nCompleted\nCancelled",
    },
    {
      fieldname: "from_time",
      label: "From Time",
      fieldtype: "Time",
    },
    {
      fieldname: "to_time",
      label: "To Time",
      fieldtype: "Time",
    },
  ],
};
