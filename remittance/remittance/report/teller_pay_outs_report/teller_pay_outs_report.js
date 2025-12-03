// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Teller Pay-outs report"] = {
	filters: [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
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
			"fieldname": "teller",
			"label": __("Pay-out Teller"),
			"fieldtype": "Link",
			"options": "Teller",
		},
		// {
		// 	"fieldname": "withdrawn_branch",
		// 	"label": __("Pay-out Branch"),
		// 	"fieldtype": "Link",
		// 	"options": "Branch",
		// },
	],
};
