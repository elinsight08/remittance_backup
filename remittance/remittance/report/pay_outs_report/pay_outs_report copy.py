# backup of pay_outs_report.py On 2025-10-24 09:33:45 from server
# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

from frappe import _
from datetime import datetime
import frappe

def execute(filters: dict | None = None):
    """Return columns and data for the report."""
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    return columns, data + [[""] * len(columns)] + [summary]

def get_columns() -> list[dict]:
    """Return columns for the report."""
    return [
        {"label": _("Date and Time"), "fieldname": "withdrawal_date", "fieldtype": "Datetime"},
        {"label": _("Name of Sending Customer"), "fieldname": "sender_name", "fieldtype": "Data"},
        {"label": _("Reference Number"), "fieldname": "name", "fieldtype": "Data"},
        {"label": _("Name of Receiver"), "fieldname": "receiver_name", "fieldtype": "Data"},
        {"label": _("Pay-out Teller"), "fieldname": "withdrawn_by", "fieldtype": "Data"},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data"},
        {"label": _("Transaction Total"), "fieldname": "amount", "fieldtype": "Currency"},
    ]

def get_data(filters: dict | None) -> list[list]:
    """Return data for the report."""
    conditions = []
    parameters = {}

    if "Super Admin" in frappe.get_roles() or "Administrator" in frappe.get_roles():
        # No filters applied for Super User or Administrator
        pass
    elif "Till Operator" in frappe.get_roles():
        # Filter by the current user (teller name)
        teller_name = frappe.session.user
        conditions.append("withdrawn_by = %(teller)s")
        parameters["teller"] = teller_name



    # Validate filters and construct conditions
    if filters:
        if filters.get("from_date"):
            print("_______________>",filters["from_date"])
            conditions.append("withdrawal_date >= %(from_date)s")
            parameters["from_date"] = filters["from_date"]
        if filters.get("to_date"):
            conditions.append("withdrawal_date <= %(to_date)s")
            parameters["to_date"] = filters["to_date"]
        if filters.get("status"):
            conditions.append("transaction_status = %(status)s")
            parameters["status"] = filters["status"]
        if filters.get("teller"):
            conditions.append("withdrawn_by = %(teller)s")
            parameters["teller"] = filters["teller"]


    # Combine conditions into a single string
    conditions_str = " AND ".join(conditions)

    # Construct the SQL query
    query = f"""
        SELECT
            withdrawal_date,
            sender_name,
            name,
            receiver_name,
            withdrawn_by,
            receiver_amount,
            charge,
            amount,
            transaction_status,
            reversed_with_charge
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 AND cash_out = 1 {('AND ' + conditions_str) if conditions_str else ''}
    """

    # Execute the query and fetch results
    data = frappe.db.sql(query, parameters, as_dict=True)

    # Return the data in the expected format
    return [[
        d.withdrawal_date,
        d.sender_name,
        d.name,
        d.receiver_name,
        d.withdrawn_by,
        d.transaction_status,
        d.amount if d.reversed_with_charge == 1 else d.receiver_amount
    ] for d in data]

def get_summary(data: list[list]) -> list:
    """Return summary row for totals and metadata."""

    total_transaction =  sum(row[6] for row in data)
    pay_in_count = len(data)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return [
        f"Summary as of {generated_at}",
        "",
        "",
        "",
        "",
        f"Pay-ins: {pay_in_count}",
        f"Total Transaction: {total_transaction:.2f}"
    ]





