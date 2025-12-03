// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Reversal Report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "sender_name",
			label: __("Sender Name"),
			fieldtype: "Data",
		},
		{
			fieldname: "receiver_name",
			label: __("Receiver Name"),
			fieldtype: "Data",
		},
		{
			fieldname: "created_till",
			label: __("Originated Till"),
			fieldtype: "Data",
		},
		{
			fieldname: "owner",
			label: __("Originated By"),
			fieldtype: "Data",
		}
	]
};
