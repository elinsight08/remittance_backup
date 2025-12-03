// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.query_reports["Aging Report"] = {
	filters: [
		 {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
		// "default": frappe.datetime.month_start()
            
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
		// "default": frappe.datetime.month_end()
            
        },
        
        
         
        {
            "fieldname": "age_bucket",
            "label": __("Age Bucket"),
            "fieldtype": "Select",
            "options": ["", "0-7", "8-14", "15-21", "22+"],
            "depends_on": "eval:doc.show_aging"
        },
        
        {
            "fieldname": "sender_name",
            "label": __("Sender Name"),
            "fieldtype": "Data"
        },
         
	],
};
