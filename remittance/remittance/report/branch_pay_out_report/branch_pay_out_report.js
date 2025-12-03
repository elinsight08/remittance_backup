// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Branch Pay-out Report"] = {
	filters: [
		{
			"fieldname": "start_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7)
		},
		{
			"fieldname": "end_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch", // Assuming you have a Branch DocType
		},
		{
			"fieldname": "teller",
			"label": __("Pay-out Teller"),
			"fieldtype": "Link",
			"options": "Teller", // Assuming tellers are User records
		}

	],
};
