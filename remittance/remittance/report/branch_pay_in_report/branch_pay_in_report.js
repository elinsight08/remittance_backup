// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Branch Pay-in report"] = {
    filters: [
        {
            "fieldname": "start_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
            "reqd": 1,
        },
        {
            "fieldname": "end_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Pending", "Completed", "Cancelled", "Reversed", "Pending Reversal"],
        },
        {
            "fieldname": "created_branch",
            "label": __("Branch"),
            "fieldtype": "Link",
            "options": "Branch",  // Link to Branch Doctype

        }
    ],
};
