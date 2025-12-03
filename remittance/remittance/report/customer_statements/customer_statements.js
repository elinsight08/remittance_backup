// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Statements"] = {
	filters: [
		{
			"fieldname": "from_date",
			"label": "From",
			"fieldtype": "Date",
			"default": null,
			"reqd": 0,
			"wildcard_filter": 0,
			"on_change": function(report) {
				validate_date_range(report);
			}
		},
		{
			"fieldname": "to_date",
			"label": "To",
			"fieldtype": "Date",
			"default": null,
			"reqd": 0,
			"wildcard_filter": 0,
			"on_change": function(report) {
				validate_date_range(report);
			}
		},
		{
			"fieldname": "sender_name",
			"label": "Customer Name",
			"fieldtype": "Data",
			"default": "",
			"reqd": 0,
			"wildcard_filter": 1
		}
	],
};

function validate_date_range(report) {
	var from_date = report.get_values().from_date;
	var to_date = report.get_values().to_date;
	if (from_date && to_date && from_date > to_date) {
		frappe.msgprint(__('From Date must be before To Date'));
		report.set_filter_value('from_date', '');
	}
}
