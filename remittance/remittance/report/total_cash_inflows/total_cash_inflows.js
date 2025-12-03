// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Total cash inflows"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today()
		},
		{
			fieldname: "entity_type",
			label: __("Entity Type"),
			fieldtype: "Select",
			options: ["", "Teller", "Branch", "Corporate"],
			default: ""
		},
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Select",
			options: ["", "USD", "ZAR"],
			default: ""
		}
	],
};
