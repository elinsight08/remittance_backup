# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

from frappe import _
from frappe.utils import flt, nowdate
from datetime import datetime
import frappe

def execute(filters=None):
    """Main entry point for the report."""
    columns = get_columns()
    data = get_data(filters)
    
    # Add totals row to the data
    if data:
        totals = calculate_totals(data)
        data.append(totals)
    
    # Return columns, data, and summary
    return columns, data, None, None, get_report_summary(data)

def get_columns():
    """Define the report columns with proper formatting."""
    return [
        {"label": _("Posting Date"), "fieldname": "withdrawal_date", "fieldtype": "Datetime", "width": 150},
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Link", "options": "Transaction", "width": 120},
        {"label": _("Sender"), "fieldname": "sender_name", "fieldtype": "Data", "width": 150},
        {"label": _("Receiver"), "fieldname": "receiver_name", "fieldtype": "Data", "width": 150},
        {"label": _("Teller"), "fieldname": "withdrawn_by", "fieldtype": "Data", "width": 120},
        {"label": _("Branch"), "fieldname": "withdrawn_branch", "fieldtype": "Link", "options": "Branch", "width": 120},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data", "width": 100},
        {"label": _("Amount Sent"), "fieldname": "receiver_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Charge"), "fieldname": "charge", "fieldtype": "Currency", "width": 100},
        {"label": _("Total Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters=None):
    """Fetch and return transaction data with proper filtering."""
    conditions = []
    params = {}
    
    # Apply role-based filters
    if not ("Administrator" in frappe.get_roles() or "Super Admin" in frappe.get_roles()):
        if "Till Operator" in frappe.get_roles():
            conditions.append("withdrawn_by = %(teller)s")
            params["teller"] = frappe.session.user
        elif "Branch Manager" in frappe.get_roles():
            branch = frappe.db.get_value("User", frappe.session.user, "branch")
            if branch:
                conditions.append("withdrawn_branch = %(branch)s")
                params["branch"] = branch

    # Apply date and other filters
    if filters:
        if filters.get("from_date"):
            conditions.append("withdrawal_date >= %(from_date)s")
            params["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions.append("withdrawal_date <= %(to_date)s")
            params["to_date"] = filters["to_date"]
        if filters.get("status"):
            conditions.append("transaction_status = %(status)s")
            params["status"] = filters["status"]
        if filters.get("teller"):
            conditions.append("withdrawn_by = %(teller)s")
            params["teller"] = filters["teller"]

    # Build and execute query
    query = """
        SELECT
            withdrawal_date,
            name,
            sender_name,
            receiver_name,
            withdrawn_by,
            withdrawn_branch,
            receiver_amount,
            COALESCE(charge, 0) as charge,
            amount,
            transaction_status
        FROM `tabTransaction`
        WHERE docstatus = 1 AND cash_out = 1
        {conditions}
        ORDER BY creation DESC
    """.format(conditions=" AND " + " AND ".join(conditions) if conditions else "")

    return frappe.db.sql(query, params, as_dict=True)

def calculate_totals(data):
    """Calculate and return totals for all numeric columns."""
    totals = {
        "withdrawal_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": "",
        "sender_name": "",
        "receiver_name": "",
        "withdrawn_by": "",
        "withdrawn_branch": _("Total"),
        "receiver_amount": sum(flt(d["receiver_amount"]) for d in data),
        "charge": sum(flt(d["charge"]) for d in data),
        "amount": sum(flt(d["amount"]) for d in data),
        "transaction_status": "",
        "bold": 1,
        "indicator": "blue"
    }
    return totals

def get_report_summary(data):
    """Generate summary cards for the report."""
    if not data:
        return []
    
    # Exclude the totals row if present
    transaction_data = [d for d in data if not d.get("bold")]
    
    return [
        {
            "label": _("Total Transactions"),
            "value": len(transaction_data),
            "indicator": "blue",
            "datatype": "Int"
        },
        {
            "label": _("Total Amount Sent"),
            "value": sum(flt(d["receiver_amount"]) for d in transaction_data),
            "indicator": "green",
            "datatype": "Currency"
        },
        {
            "label": _("Total Charges"),
            "value": sum(flt(d["charge"]) for d in transaction_data),
            "indicator": "red",
            "datatype": "Currency"
        }
    ]