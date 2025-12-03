// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Corporate Branch Cash Ins - Cash Out Report"] = {
	filters: [
		{
      "fieldname": "from_date",
      "label": "From Date",
      "fieldtype": "Date",
      "default": frappe.datetime.month_start(),
      "reqd": 1
    },
    {
      "fieldname": "to_date",
      "label": "To Date",
      "fieldtype": "Date",
      "default": frappe.datetime.month_end(),
      "reqd": 1
    },
    {
      "fieldname": "branch",
      "label": "Branch",
      "fieldtype": "Link",
      "options": "Branch",
		"reqd": 1
    },
    {
      "fieldname": "till",
      "label": "Till",
      "fieldtype": "Link",
      "options": "Till"
    }
	],
};
