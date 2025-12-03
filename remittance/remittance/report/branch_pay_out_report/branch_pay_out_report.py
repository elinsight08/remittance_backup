# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import flt
from typing import Optional

def execute(filters: Optional[dict] = None):
    columns = get_columns()
    data = get_data(filters)
    
    # Calculate totals
    total_sender = flt(sum(row.get("amount", 0) for row in data if not row.get("is_total_row")))
    total_receiver = flt(sum(row.get("receiver_amount", 0) for row in data if not row.get("is_total_row")))
    total_charge = flt(sum(row.get("charge", 0) for row in data if not row.get("is_total_row")))
    total_count = len([row for row in data if not row.get("is_total_row")])
    
    # Add totals row
    if data:
        totals_row = {
            "creation": "",
            "sender_name": _("TOTAL"),
            "name": "",
            "receiver_name": "",
            "transaction_status": "",
            "withdrawn_by": "",
            "withdrawn_branch": "",
            "amount": total_sender,
            "receiver_amount": total_receiver,
            "charge": total_charge,
            "is_total_row": True
        }
        data.append(totals_row)
    
    return columns, data

def get_columns() -> list[dict]:
    return [
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Datetime", "width": 160},
        {"label": _("Sending Customer"), "fieldname": "sender_name", "fieldtype": "Data", "width": 150},
        {"label": _("Reference Number"), "fieldname": "name", "fieldtype": "Data", "width": 130},
        {"label": _("Receiver"), "fieldname": "receiver_name", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data", "width": 120},
        {"label": _("Pay-out Teller"), "fieldname": "withdrawn_by", "fieldtype": "Link", "options": "Teller", "width": 130},
        {"label": _("Pay-out Agent and Branch"), "fieldname": "withdrawn_branch", "fieldtype": "Link", "options": "Branch", "width": 180},
        {"label": _("Sender Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Receiver Amount"), "fieldname": "receiver_amount", "fieldtype": "Currency", "width": 150},
        {"label": _("Charge"), "fieldname": "charge", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters: Optional[dict] = None):
    conditions = []
    parameters = {}
    
    # Role-based filtering
    if "Super Admin" not in frappe.get_roles() and "Administrator" not in frappe.get_roles():
        if "Branch Manager" in frappe.get_roles():
            user = frappe.get_doc("User", frappe.session.user)
            if user and user.branch:
                conditions.append("withdrawn_branch = %(branch)s")
                parameters["branch"] = user.branch

    # Apply filters
    if filters:
        if filters.get("start_date"):
            conditions.append("posting_date >= %(start_date)s")
            parameters["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            conditions.append("posting_date <= %(end_date)s")
            parameters["end_date"] = filters["end_date"]
        if filters.get("status"):
            conditions.append("transaction_status = %(status)s")
            parameters["status"] = filters["status"]
        if filters.get("branch"):
            conditions.append("withdrawn_branch = %(branch)s")
            parameters["branch"] = filters["branch"]
        if filters.get("teller"):
            conditions.append("withdrawn_by = %(teller)s")
            parameters["teller"] = filters["teller"]

    # Build query
    query = f"""
        SELECT
            posting_date,
            sender_name,
            name,
            receiver_name,
            transaction_status,
            withdrawn_by,
            withdrawn_branch,
            amount as amount,
            receiver_amount,
            charge
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 AND cash_out = 1 {('AND ' + ' AND '.join(conditions)) if conditions else ''}
        ORDER BY
            posting_date DESC
    """

    data = frappe.db.sql(query, parameters, as_dict=True)
    
    return data