// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Corporate Pay-ins Report"] = {
filters: [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "branch",
			"label": __("Pay-in Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		// {
		// 	"fieldname": "teller",
		// 	"label": __("Teller"),
		// 	"fieldtype": "Link",
		// 	"options": "User"
		// }
	]
};

