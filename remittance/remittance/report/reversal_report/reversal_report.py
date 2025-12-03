from frappe import _
import frappe
from frappe.utils import getdate, nowdate, flt

def execute(filters=None):
    filters = frappe._dict(filters or {})
    setup_default_filters(filters)
    
    # Apply user branch filter if user has branch assigned
    if not filters.get("branch") and frappe.session.user != "Administrator":
        user_branch = frappe.db.get_value("User", frappe.session.user, "branch")
        if user_branch:
            filters.branch = user_branch
    
    columns = get_columns()
    data = get_data(filters)
    
    if data:
        data = add_total_row(data)
    
    return columns, data, None, None, get_report_summary(data)

def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT 
            t.posting_date,
            r.transaction_id,
            r.sender_name,
            r.receiver,
            r.owner,
            r.branch,
            t.created_till,
            t.amount as original_amount,
            t.reversed_with_charge,
            t.charge as charge,
            CASE 
                WHEN t.reversed_with_charge = 1 THEN t.amount 
                ELSE r.receiver_amount 
            END as reversed_amount,
            CASE
                WHEN t.reversed_with_charge = 1 THEN (t.amount - r.receiver_amount)
                ELSE 0.00
            END as charge_amount,
            r.posting_date AS reversal_date,
            r.modified_by,
            r.name AS reversal_id
        FROM 
            `tabReversal` r
        JOIN 
            `tabTransaction` t ON t.name = r.transaction_id
        WHERE 
            t.docstatus = 1
            AND r.docstatus = 1
            {conditions}
        ORDER BY 
            r.posting_date DESC
    """, filters, as_dict=True)
    
    return data

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("r.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("r.posting_date <= %(to_date)s")
    if filters.get("sender_name"):
        conditions.append("r.sender_name LIKE %(sender_name)s")
        filters["sender_name"] = f"%{filters.sender_name}%"
    if filters.get("receiver_name"):
        conditions.append("r.receiver LIKE %(receiver_name)s")
        filters["receiver_name"] = f"%{filters.receiver_name}%"
    if filters.get("created_till"):
        conditions.append("LOWER(t.created_till) LIKE %(created_till)s")
        filters["created_till"] = f"%{filters.created_till.lower()}%"
        
    if filters.get("branch"):
        conditions.append("r.branch = %(branch)s")
    if filters.get("owner"):
        conditions.append("r.owner = %(owner)s")
    
    return " AND " + " AND ".join(conditions) if conditions else ""

def add_total_row(data):
    total_original = sum(flt(d.get("original_amount", 0)) for d in data)
    total_reversed = sum(flt(d.get("reversed_amount", 0)) for d in data)
    total_charge = sum(flt(d.get("charge", 0)) for d in data)
    
    total_row = {
        "branch": _("GRAND TOTAL"),
        "original_amount": total_original,
        "reversed_amount": total_reversed,
        "charge": total_charge,
        "indicator": "red",
        "bold": 1
    }
    
    return data + [total_row]

def get_report_summary(data):
    if not data:
        return None
    
    total_reversed = sum(flt(d.get("reversed_amount", 0)) for d in data if not d.get("indicator"))
    total_charge = sum(flt(d.get("charge_amount", 0)) for d in data if not d.get("indicator"))
    total_reversals = len([d for d in data if not d.get("indicator")])
    
    return [
        {
            "value": total_reversals,
            "label": _("Total Reversals"),
            "indicator": "red",
            "datatype": "Int"
        },
        {
            "value": total_reversed,
            "label": _("Total Amount Reversed"),
            "indicator": "red",
            "datatype": "Currency"
        },
        {
            "value": total_charge,
            "label": _("Total Charges"),
            "indicator": "blue",
            "datatype": "Currency"
        }
    ]

def setup_default_filters(filters):
    if not filters.get("from_date") and not filters.get("to_date"):
        filters.from_date = frappe.utils.get_first_day(nowdate())
        filters.to_date = frappe.utils.get_last_day(nowdate())
    elif filters.get("from_date") and not filters.get("to_date"):
        filters.to_date = nowdate()
    elif filters.get("to_date") and not filters.get("from_date"):
        filters.from_date = frappe.utils.add_months(filters.to_date, -1)

def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": _("Original Date"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "transaction_id",
            "label": _("Transaction ID"),
            "fieldtype": "Link",
            "options": "Transaction",
            "width": 120
        },
        {
            "fieldname": "sender_name",
            "label": _("Sender"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "receiver",
            "label": _("Receiver"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "owner",
            "label": _("Initiated By"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "branch",
            "label": _("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "width": 120
        },
        {
            "fieldname": "created_till",
            "label": _("Till Originated"),
            "width": 120
        },
        {
            "fieldname": "reversal_date",
            "label": _("Reversal Date"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "modified_by",
            "label": _("Approved By"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "original_amount",
            "label": _("Original Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "reversed_amount",
            "label": _("Reversed Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "charge",
            "label": _("Charge"),
            "fieldtype": "Currency",
            "width": 100,
            "default": "0.00"
        },
        {
            "fieldname": "reversed_with_charge",
            "label": _("With Charges"),
            "fieldtype": "Check",
            "width": 100
        }
    ]