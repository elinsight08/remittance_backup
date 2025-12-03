// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Cash Movement"] = {
	filters: [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company"),
			"width": "80"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "80"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nDraft\nSubmitted\nCancelled",
			"default": "Submitted",
			"width": "80"
		},
		{
			"fieldname": "source_type",
			"label": __("Source Type"),
			"fieldtype": "Select",
			"options": "\nBranch\nTill\nAgent",
			"width": "100",
			"on_change": function() {
				// Dynamically update source options based on source_type
				let source_type = frappe.query_report.get_filter_value('source_type');
				let source_filter = frappe.query_report.get_filter('source');

				if (source_type) {
					source_filter.df.options = source_type;
					source_filter.df.reqd = 0;
					source_filter.refresh();
				}
			}
		},
		{
			"fieldname": "source",
			"label": __("Source"),
			"fieldtype": "Dynamic Link",
			"options": "source_type",
			"width": "100",
			"get_query": function() {
				let source_type = frappe.query_report.get_filter_value('source_type');
				if (!source_type) {
					frappe.msgprint(__("Please select Source Type first"));
					return;
				}
				return {
					"doctype": source_type
				};
			}
		},
		{
			"fieldname": "destination_type",
			"label": __("Destination Type"),
			"fieldtype": "Select",
			"options": "\nBranch\nTill\nAgent",
			"width": "100",
			"on_change": function() {
				// Dynamically update destination options based on destination_type
				let dest_type = frappe.query_report.get_filter_value('destination_type');
				let dest_filter = frappe.query_report.get_filter('destination');

				if (dest_type) {
					dest_filter.df.options = dest_type;
					dest_filter.df.reqd = 0;
					dest_filter.refresh();
				}
			}
		},
		{
			"fieldname": "destination",
			"label": __("Destination"),
			"fieldtype": "Dynamic Link",
			"options": "destination_type",
			"width": "100",
			"get_query": function() {
				let dest_type = frappe.query_report.get_filter_value('destination_type');
				if (!dest_type) {
					frappe.msgprint(__("Please select Destination Type first"));
					return;
				}
				return {
					"doctype": dest_type
				};
			}
		},
		{
			"fieldname": "currency",
			"label": __("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"default": frappe.defaults.get_user_default("currency"),
			"width": "80"
		},
		{
			"fieldname": "default_branch",
			"label": __("Default Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100"
		}
	]
};
