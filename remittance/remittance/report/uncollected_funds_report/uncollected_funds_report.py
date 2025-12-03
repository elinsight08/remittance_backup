from frappe import _
import frappe
from frappe.utils import getdate, nowdate, flt

def execute(filters=None):
    filters = frappe._dict(filters or {})
    setup_default_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    
    # Add total row if data exists
    if data:
        data = add_total_row(data)
    
    message = get_report_summary(data)
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)
    
    return columns, data, message, chart, report_summary

def add_total_row(data):
    """Adds a total row at the end of the data"""
    total_amount = sum(flt(d.get("amount", 0)) for d in data)
    total_transactions = len(data)
    
    total_row = {
        "posting_date": _("GRAND TOTAL"),
        "amount": total_amount,
        "indicator": "red",
        "bold": True,
        "is_total_row": True
    }
    
    return data + [total_row]

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
            "label": _("Posting Date"),
            "fieldtype": "DateTime",
            "width": 150
        },
        {
            "fieldname": "name",
            "label": _("Transaction ID"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "sender_name",
            "label": _("Sender Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "receiver_name",
            "label": _("Receiver Name"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "owner",
            "label": _("Pay in Teller"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "till",
            "label": _("Till"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "created_branch",
            "label": _("Branch"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 80,
            "show_total": True
        },
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    # Initialize parameters
    parameters = filters.copy()
    
    # For Till Operator role, filter by current user and their branch
    # if "Till Operator" not in frappe.get_roles():
    #     user = frappe.get_doc("User", frappe.session.user)
    #     parameters["teller"] = user.name
        
    # Get the branch associated with the user
    user = frappe.get_doc("User", frappe.session.user)

    if hasattr(user, 'branch'):
        parameters["created_branch"] = user.branch
        conditions.append("created_branch = %(created_branch)s")
    
   
    
    data = frappe.db.sql(f"""
        SELECT 
            posting_date,
            name,
            sender_name,
            receiver_name,
            owner,
            created_till as till,
            created_branch,
            amount,
            transaction_status as status
        FROM 
            `tabTransaction`
        WHERE 
            docstatus = 1 
            AND (transaction_status = 'Pending' OR transaction_status = 'Pending Reversal') 
            {' AND ' + ' AND '.join(conditions) if conditions else ''}
        ORDER BY 
            posting_date DESC, created_branch
    """, parameters, as_dict=True)

    return data

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("sender_name"):
        conditions.append("sender_name LIKE %(sender_name)s")
        filters["sender_name"] = f"%{filters.sender_name}%"
    if filters.get("receiver_name"):
        conditions.append("receiver_name LIKE %(receiver_name)s")
        filters["receiver_name"] = f"%{filters.receiver_name}%"
    # if filters.get("created_branch") and "Till Operator" not in frappe.get_roles():
    #     conditions.append("created_branch = %(created_branch)s")
    # if filters.get("owner") and "Till Operator" not in frappe.get_roles():
    #     conditions.append("owner LIKE %(owner)s")
    #     filters["owner"] = f"%{filters.owner}%"
    if filters.get("created_branch"):
        conditions.append("created_branch = %(created_branch)s")
    if filters.get("owner"):
        conditions.append("owner LIKE %(owner)s")
        filters["owner"] = f"%{filters.owner}%"
    if filters.get("created_till"):
        conditions.append("created_till LIKE %(created_till)s")
        filters["created_till"] = f"%{filters.created_till}%"
    
    return conditions

def get_report_summary(data):
    if not data:
        return None
    
    total_amount = sum(flt(d.get("amount", 0)) for d in data if not d.get("is_total_row"))
    total_transactions = len([d for d in data if not d.get("is_total_row")])
    
    return [
        {
            "value": total_transactions,
            "label": _("Total Transactions"),
            "indicator": "Red",
            "datatype": "Int"
        },
        {
            "value": total_amount,
            "label": _("Total Amount"),
            "indicator": "Red",
            "datatype": "Currency"
        },
        {
            "value": frappe.utils.fmt_money(total_amount / total_transactions if total_transactions else 0),
            "label": _("Average Amount per Transaction"),
            "indicator": "Blue",
            "datatype": "Currency"
        }
    ]

def get_chart_data(data):
    if not data:
        return None
    
    # Group by branch for chart
    branch_totals = {}
    for d in data:
        if d.get("is_total_row"):
            continue
        branch = d.created_branch or "Unknown"
        branch_totals.setdefault(branch, 0)
        branch_totals[branch] += flt(d.get("amount", 0))
    
    return {
        # "data": {
        #     "labels": list(branch_totals.keys()),
        #     "datasets": [{
        #         "name": "Amount by Branch",
        #         "values": list(branch_totals.values())
        #     }]
        # },
        # "type": "bar",
        # "colors": ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56"],
        # "barOptions": {
        #     "stacked": False
        # }
    }