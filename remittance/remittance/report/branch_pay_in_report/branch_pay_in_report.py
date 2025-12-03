# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime

def execute(filters: dict | None = None):
    columns = get_columns()
    data, summary = get_data(filters)
    return columns, data, None, summary  # 'None' is for chart, last is summary

def get_columns() -> list[dict]:
    return [
        {"label": _("Date and Time"), "fieldname": "creation", "fieldtype": "Datetime"},
        {"label": _("Pay-in Teller"), "fieldname": "owner", "fieldtype": "Link", "options": "User"},
        {"label": _("Sending Customer"), "fieldname": "sender_name", "fieldtype": "Data"},
        {"label": _("Reference Number"), "fieldname": "name", "fieldtype": "Data"},
        {"label": _("Receiver"), "fieldname": "receiver_name", "fieldtype": "Data"},
        {"label": _("Source/Destination Amount"), "fieldname": "receiver_amount", "fieldtype": "Currency"},
        {"label": _("Commission"), "fieldname": "charge", "fieldtype": "Currency"},
        {"label": _("Transaction Total"), "fieldname": "amount", "fieldtype": "Currency"},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Select", "options": "Collected\nNot Collected"},
        {"label": _("Branch"), "fieldname": "created_branch", "fieldtype": "Link", "options": "Branch"},  # Added Branch column
    ]

def get_data(filters: dict | None = None):
    conditions = []
    parameters = {}
    
    if "Super Admin" in frappe.get_roles() or "Administrator" in frappe.get_roles():
        # No filters applied for Super User or Administrator
        pass
    elif "Branch Manager" in frappe.get_roles():
        # Filter by the current user (teller name)
        user = frappe.get_doc("User", frappe.session.user)
        if user and user.branch:
            branch = user.branch
            conditions.append("created_branch =  %(created_branch)s")
            parameters["created_branch"] = branch

    # Validate filters and construct conditions
    if filters:
        if filters.get("start_date"):
            conditions.append("creation >= %(start_date)s")
            parameters["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            conditions.append("creation <= %(end_date)s")
            parameters["end_date"] = filters["end_date"]
        if filters.get("status"):
            conditions.append("transaction_status = %(status)s")
            parameters["status"] = filters["status"]
        if filters.get("created_branch"):
            conditions.append("created_branch = %(created_branch)s")
            parameters["created_branch"] = filters["created_branch"]

    # Combine conditions into a single string
    conditions_str = " AND ".join(conditions)

    # Construct the SQL query
    query = f"""
        SELECT
            creation,
            owner,
            sender_name,
            name,
            receiver_name,
            receiver_amount,
            charge,
            amount,
            transaction_status,
            created_branch
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 AND cash_in = 1 {('AND ' + conditions_str) if conditions_str else ''}
    """

    # Execute the query and fetch results
    data = frappe.db.sql(query, parameters, as_dict=True)

    # Compute totals per teller
    teller_summary = {}
    for row in data:
        teller = row["owner"]
        if teller not in teller_summary:
            teller_summary[teller] = {"amount": 0, "commission": 0, "total": 0, "count": 0}
        teller_summary[teller]["amount"] += row["receiver_amount"]
        teller_summary[teller]["commission"] += row["charge"]
        teller_summary[teller]["total"] += row["amount"]
        teller_summary[teller]["count"] += 1

    # Branch total
    branch_summary = {"amount": 0, "commission": 0, "total": 0, "count": 0}
    for s in teller_summary.values():
        branch_summary["amount"] += s["amount"]
        branch_summary["commission"] += s["commission"]
        branch_summary["total"] += s["total"]
        branch_summary["count"] += s["count"]

    summary = []
    for teller, stats in teller_summary.items():
        summary.append(
            {
                "label": f"Teller: {teller}",
                "value": f"Total Amount: {stats['amount']:.2f}, Commission: {stats['commission']:.2f}, "
                         f"Total: {stats['total']:.2f}, Transactions: {stats['count']}"
            }
        )

    summary.append({"label": "Branch Totals", "value": f"Total Amount: {branch_summary['amount']:.2f}, "
                                                       f"Commission: {branch_summary['commission']:.2f}, "
                                                       f"Total: {branch_summary['total']:.2f}, "
                                                       f"Transactions: {branch_summary['count']}"})
    summary.append({"label": "Generated At", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    return data, summary
