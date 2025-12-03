// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Agent Commission Report"] = {
	filters: [
		 {
      "fieldname": "from_date",
      "label": "From Date",
      "fieldtype": "Date",
      "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
      "reqd": 1
    },
    {
      "fieldname": "to_date",
      "label": "To Date",
      "fieldtype": "Date",
      "default": frappe.datetime.get_today(),
      "reqd": 1
    },
    {
      "fieldname": "agent",
      "label": "Agent",
      "fieldtype": "Link",
      "options": "Agent"
    }
	],
};
