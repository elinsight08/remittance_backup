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
        {"label": _("Date and Time"), "fieldname": "posting_date", "fieldtype": "Datetime"},
        {"label": _("Name of Sending Customer"), "fieldname": "sender_name", "fieldtype": "Data"},
        {"label": _("Reference Number"), "fieldname": "name", "fieldtype": "Data"},
        {"label": _("Name of Receiver"), "fieldname": "receiver_name", "fieldtype": "Data"},
        {"label": _("Pay-in Teller"), "fieldname": "owner", "fieldtype": "Data"},
        {"label": _("Destination Amount"), "fieldname": "receiver_amount", "fieldtype": "Currency"},
        {"label": _("Commission"), "fieldname": "charge", "fieldtype": "Currency"},
        {"label": _("Transaction Total"), "fieldname": "amount", "fieldtype": "Currency"},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data"},
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
        conditions.append("owner = %(teller)s")
        parameters["teller"] = teller_name

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
            conditions.append("posting_date >= %(start_date)s")
            parameters["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            conditions.append("posting_date <= %(end_date)s")
            parameters["end_date"] = filters["end_date"]
        if filters.get("status"):
            conditions.append("transaction_status = %(status)s")
            parameters["status"] = filters["status"]
        if filters.get("teller"):
            conditions.append("owner = %(teller)s")
            parameters["teller"] = filters["teller"]
        if filters.get("created_branch"):
            conditions.append("created_branch = %(created_branch)s")
            parameters["created_branch"] = filters["created_branch"]

    # Combine conditions into a single string
    conditions_str = " AND ".join(conditions)

    # Construct the SQL query
    query = f"""
        SELECT
            posting_date,
            sender_name,
            name,
            receiver_name,
            owner,
            receiver_amount,
            charge,
            amount,
            transaction_status
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 AND cash_in = 1 {('AND ' + conditions_str) if conditions_str else ''}
    """

    # Execute the query and fetch results
    data = frappe.db.sql(query, parameters, as_dict=True)

    # Return the data in the expected format
    return [[
        d.posting_date,
        d.sender_name,
        d.name,
        d.receiver_name,
        d.owner,
        d.receiver_amount,
        d.charge,
        d.amount,
        d.transaction_status
    ] for d in data]

def get_summary(data: list[list]) -> list:
    """Return summary row for totals and metadata."""
    total_amount = sum(row[5] for row in data)
    total_commission = sum(row[6] for row in data)
    total_transaction = sum(row[7] for row in data)
    pay_in_count = len(data)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return [
        f"Summary as of {generated_at}",
        "",
        "",
        "",
        "",
        f"Total Amount: {total_amount:.2f}",
        f"Total Commission: {total_commission:.2f}",
        f"Total Transaction: {total_transaction:.2f}",
        f"Pay-ins: {pay_in_count}"
    ]







# # Copyright (c) 2025, Tafadzwa Barwa and contributors
# # For license information, please see license.txt

# from frappe import _
# from datetime import datetime
# import frappe

# def execute(filters: dict | None = None):
#     """Return columns and data for the report."""
#     columns = get_columns()
#     data = get_data(filters)
#     summary = get_summary(data)
#     return columns, data + [[""] * len(columns)] + [summary]

# def get_columns() -> list[dict]:
#     """Return columns for the report."""
#     return [
#         {"label": _("Date and Time"), "fieldname": "posting_date", "fieldtype": "Datetime"},
#         {"label": _("Name of Sending Customer"), "fieldname": "sender_name", "fieldtype": "Data"},
#         {"label": _("Reference Number"), "fieldname": "name", "fieldtype": "Data"},
#         {"label": _("Name of Receiver"), "fieldname": "receiver_name", "fieldtype": "Data"},
#         {"label": _("Destination Amount"), "fieldname": "receiver_amount", "fieldtype": "Currency"},
#         {"label": _("Commission"), "fieldname": "charge", "fieldtype": "Currency"},
#         {"label": _("Transaction Total"), "fieldname": "amount", "fieldtype": "Currency"},
#         {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data"},
#     ]

# def get_data(filters: dict | None) -> list[list]:
#     """Return data for the report."""
#     # Query to fetch transaction data
#     conditions = ""
#     if filters and filters.get("date"):
#         conditions += " and posting_date >= %(start_date)s and posting_date <= %(end_date)s"

#     query = """
#         SELECT
#             posting_date,
#             sender_name,
#             name,
#             receiver_name,
#             receiver_amount,
#             charge,
#             amount,
#             transaction_status
#         FROM
#             `tabTransaction`
#         WHERE
#             docstatus = 1 {conditions}
#     """.format(conditions=conditions)

#     data = frappe.db.sql(query, filters, as_dict=True)
#     return [[d.posting_date, d.sender_name, d.name, d.receiver_name, d.receiver_amount, d.charge, d.amount, d.transaction_status] for d in data]

# def get_summary(data: list[list]) -> list:
#     """Return summary row for totals and metadata."""
#     total_amount = sum(row[4] for row in data)
#     total_commission = sum(row[5] for row in data)
#     total_transaction = sum(row[6] for row in data)
#     pay_in_count = len(data)
#     generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     return [
#         f"Summary as of {generated_at}",
#         "",
#         "",
#         "",
#         f"Total Amount: {total_amount:.2f}",
#         f"Total Commission: {total_commission:.2f}",
#         f"Total Transaction: {total_transaction:.2f}",
#         f"Pay-ins: {pay_in_count}"
#     ]
