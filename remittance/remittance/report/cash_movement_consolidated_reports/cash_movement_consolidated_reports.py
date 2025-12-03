from frappe import _
import frappe
from frappe.utils import getdate, nowdate, flt

def execute(filters=None):
    filters = frappe._dict(filters or {})
    setup_default_filters(filters)
    
    # Apply user branch filter if not admin
    if not filters.get("branch") and "System Manager" not in frappe.get_roles():
        user_branch = frappe.db.get_value("User", frappe.session.user, "branch")
        if user_branch:
            filters.branch = user_branch
    
    columns = get_columns()
    data = get_data(filters)
    
    if data:
        data = add_totals(data)
    
    chart = get_chart_data(data)
    report_summary = get_report_summary(data)
    
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "transaction_type",
            "label": _("Transaction Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "from_location",
            "label": _("From"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "to_location",
            "label": _("To"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "reference_no",
            "label": _("Reference"),
            "fieldtype": "Dynamic Link",
            "options": "reference_doctype",
            "width": 120
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    # conditions = get_conditions(filters)
    
    # # Get all cash movement transactions
    # data = frappe.db.sql(f"""
    #     SELECT 
    #         posting_date,
            
    #         from_till as from_location,
    #         to_till as to_location,
    #         name as reference_no,
    #         'Cash Movement' as reference_doctype,
    #         amount,
    #         status
    #     FROM `tabFloat Allocation`
    #     WHERE docstatus = 1 {conditions}
        
    #     UNION ALL
        
    #     SELECT 
    #         posting_date,
    #         'Interbranch Transfer' as transaction_type,
    #         from_branch as from_location,
    #         to_branch as to_location,
    #         name as reference_no,
    #         'Interbranch Transfer' as reference_doctype,
    #         amount,
    #         status
    #     FROM `tabInterbranch Transfer`
    #     WHERE docstatus = 1 {conditions}
        
    #     ORDER BY posting_date DESC
    # """, filters, as_dict=True)
    
    # # Classify transaction types
    # for row in data:
    #     if row.from_location and row.to_location:
    #         if "Teller" in row.from_location and "Teller" in row.to_location:
    #             row.transaction_type = "Inter-teller"
    #         elif "Vault" in row.from_location and "Teller" in row.to_location:
    #             row.transaction_type = "Branch Vault to Teller"
    #         elif "Vault" in row.from_location and "Corporate" in row.to_location:
    #             row.transaction_type = "Branch Vault to Corporate"
    #         elif "Corporate" in row.from_location and "Corporate" in row.to_location:
    #             row.transaction_type = "Corporate to Corporate"
    
    return []

def get_conditions(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("AND posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("AND posting_date <= %(to_date)s")
    if filters.get("branch"):
        conditions.append("AND (from_branch = %(branch)s OR to_branch = %(branch)s)")
    if filters.get("transaction_type"):
        type_conditions = {
            "Inter-teller": "AND from_till LIKE 'Teller%' AND to_till LIKE 'Teller%'",
            "Branch Vault to Teller": "AND from_till LIKE 'Vault%' AND to_till LIKE 'Teller%'",
            "Branch Vault to Corporate": "AND from_till LIKE 'Vault%' AND to_till LIKE 'Corporate%'",
            "Corporate to Corporate": "AND from_till LIKE 'Corporate%' AND to_till LIKE 'Corporate%'"
        }
        conditions.append(type_conditions.get(filters.transaction_type, ""))
    
    return " ".join(conditions)

def add_totals(data):
    # Add type-wise totals
    totals = {}
    for row in data:
        if row.transaction_type not in totals:
            totals[row.transaction_type] = 0
        totals[row.transaction_type] += flt(row.amount)
    
    # Add total rows
    total_rows = []
    for ttype, amount in totals.items():
        total_rows.append({
            "transaction_type": _(f"{ttype} Total"),
            "amount": amount,
            "indicator": "blue",
            "bold": 1
        })
    
    # Add grand total
    if totals:
        total_rows.append({
            "transaction_type": _("GRAND TOTAL"),
            "amount": sum(totals.values()),
            "indicator": "red",
            "bold": 1
        })
    
    return data + total_rows

def get_report_summary(data):
    if not data:
        return None
    
    totals = {}
    for row in data:
        if not row.get("reference_no"):
            continue
        if row.transaction_type not in totals:
            totals[row.transaction_type] = {"count": 0, "amount": 0}
        totals[row.transaction_type]["count"] += 1
        totals[row.transaction_type]["amount"] += flt(row.amount)
    
    summary = []
    for ttype, values in totals.items():
        summary.append({
            "value": f"{values['count']}",
            "label": _(f"{ttype} Transactions"),
            "datatype": "Int"
        })
        summary.append({
            "value": frappe.format(values["amount"], {"fieldtype": "Currency"}),
            "label": _(f"{ttype} Amount"),
            "datatype": "Currency"
        })
    
    return summary

def get_chart_data(data):
    if not data:
        return None
    
    type_amounts = {}
    for row in data:
        if not row.get("reference_no"):  # Skip total rows
            continue
        if row.transaction_type not in type_amounts:
            type_amounts[row.transaction_type] = 0
        type_amounts[row.transaction_type] += flt(row.amount)
    
    return {
        "data": {
            "labels": list(type_amounts.keys()),
            "datasets": [{
                "name": "Amount by Transaction Type",
                "values": list(type_amounts.values())
            }]
        },
        "type": "pie",
        "colors": ["#7CD6FD", "#743EE2", "#FF5858", "#FFC744"],
        "height": 300
    }

def setup_default_filters(filters):
    if not filters.get("from_date") and not filters.get("to_date"):
        filters.from_date = frappe.utils.get_first_day(nowdate())
        filters.to_date = frappe.utils.get_last_day(nowdate())
    elif filters.get("from_date") and not filters.get("to_date"):
        filters.to_date = nowdate()
    elif filters.get("to_date") and not filters.get("from_date"):
        filters.from_date = frappe.utils.add_months(filters.to_date, -1)