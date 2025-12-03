frappe.query_reports["Uncollected Funds Report"] = {
 
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
            placeholder: __("Search by sender name...")
        },
        {
            fieldname: "receiver_name",
            label: __("Receiver Name"),
            fieldtype: "Data",
            placeholder: __("Search by receiver name...")
        },
        {
            fieldname: "created_branch",
            label: __("Branch"),
            fieldtype: "Link",
            options: "Branch",
            placeholder: __("Filter by branch...")
        },
        {
            fieldname: "owner",
            label: __("Teller"),
            fieldtype: "Data",
        },
        {
            fieldname: "created_till",
            label: __("Till"),
            fieldtype: "Data",
            placeholder: __("Filter by till...")
        }
    ]
};