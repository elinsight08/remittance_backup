// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Cash Movement Consolidated Reports"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "source_type",
			label: __("Source Type"),
			fieldtype: "Select",
			options: ["", "Teller", "Branch Vault", "Corporate"],
		},
		{
			fieldname: "destination_type",
			label: __("Destination Type"),
			fieldtype: "Select",
			options: ["", "Teller", "Branch Vault", "Corporate"],
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Pending", "Completed", "Cancelled"],
		},
	],
};
