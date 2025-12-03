from frappe import _
import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    
    # Add message with totals summary
    message = get_totals_message(data)
    
    return columns, data, message

def get_columns():
    return [
        {"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 120},
        {"fieldname": "sender_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 200},
        {"fieldname": "cash_in", "label": _("Cash In"), "fieldtype": "Currency", "width": 100},
        {"fieldname": "cash_out", "label": _("Cash Out"), "fieldtype": "Currency", "width": 100},
    ]

def get_data(filters):
    # Get data from Transaction table
    data = get_transaction_data(filters)
    
    if not data:
        return []
    
    # Calculate and add group totals
    grouped_data = []
    current_group = None
    grand_total_cash_in = 0
    grand_total_cash_out = 0
    
    for row in data:
        # Initialize new group if needed
        if not current_group or current_group["sender_name"] != row["sender_name"]:
            if current_group:
                # Add group totals to the grouped_data before starting new group
                grouped_data.append(create_total_row(current_group))
                grand_total_cash_in += current_group["total_cash_in"]
                grand_total_cash_out += current_group["total_cash_out"]
            
            current_group = {
                "sender_name": row["sender_name"],
                "total_cash_in": 0,
                "total_cash_out": 0,
                "is_group": True
            }
        
        # Add current row to group
        current_group["total_cash_in"] += row["cash_in"]
        current_group["total_cash_out"] += row["cash_out"]
        grouped_data.append(row)
    
    # Add the last group's totals
    if current_group:
        grouped_data.append(create_total_row(current_group))
        grand_total_cash_in += current_group["total_cash_in"]
        grand_total_cash_out += current_group["total_cash_out"]
    
    # Add grand totals with bold formatting
    if grouped_data:
        grouped_data.append({
            "posting_date": "",
            "sender_name": _("GRAND TOTAL"),
            "cash_in": grand_total_cash_in,
            "cash_out": grand_total_cash_out,
            "bold": 1,
            "is_total": True,
            "is_grand_total": True  # Additional identifier for styling
        })
    
    return grouped_data

def get_transaction_data(filters):
    conditions = []
    params = {}
    
    # Build filter conditions
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]
    if filters.get("sender_name"):
        conditions.append("sender_name LIKE %(sender_name)s")
        params["sender_name"] = f"%{filters['sender_name']}%"
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    transactions = frappe.db.sql(f"""
        SELECT 
            posting_date,
            sender_name,
            amount as cash_in,
            receiver_amount as cash_out
        FROM 
            `tabTransaction`
        WHERE 
            docstatus = 1 AND {where_clause}
        ORDER BY 
            posting_date, sender_name
    """, params, as_dict=True)
    
    return transactions

def apply_filters(row, filters):
    match = True
    
    # Date range filtering
    if filters.get("from_date") and row["posting_date"] < filters.get("from_date"):
        match = False
    if filters.get("to_date") and row["posting_date"] > filters.get("to_date"):
        match = False
        
    # Customer name filtering with partial match
    if filters.get("sender_name"):
        search_term = filters["sender_name"].lower()
        if search_term not in row["sender_name"].lower():
            match = False
            
    return match

def create_total_row(group):
    return {
        "posting_date": "",
        "sender_name": _("Total for {0}").format(group["sender_name"]),
        "cash_in": group["total_cash_in"],
        "cash_out": group["total_cash_out"],
        "bold": 1,
        "is_group_total": True
    }

def get_totals_message(data):
    grand_total = next((row for row in data if row.get("is_grand_total")), None)
    if grand_total:
        return _("Grand Total: Cash In = {0}, Cash Out = {1}").format(
            frappe.format_value(grand_total["cash_in"], {"fieldtype": "Currency"}),
            frappe.format_value(grand_total["cash_out"], {"fieldtype": "Currency"})
        )
    return ""