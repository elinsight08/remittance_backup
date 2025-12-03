# # Copyright (c) 2025, Tafadzwa Barwa and contributors
# # For license information, please see license.txt

# from frappe import _


# def execute(filters: dict | None = None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data


# def get_columns() -> list[dict]:
#     return [
#         {
#             "label": _("Date"),
#             "fieldname": "date",
#             "fieldtype": "Date",
#             "width": 120,
#         },
#         {
#             "label": _("Pay-in Branch"),
#             "fieldname": "branch_name",
#             "fieldtype": "Data",
#             "width": 180,
#         },
#         {
#             "label": _("Source/Destination Amount"),
#             "fieldname": "amount",
#             "fieldtype": "Currency",
#             "width": 150,
#         },
#         {
#             "label": _("Commission Paid"),
#             "fieldname": "commission",
#             "fieldtype": "Currency",
#             "width": 130,
#         },
#         {
#             "label": _("No. of Transactions"),
#             "fieldname": "transaction_count",
#             "fieldtype": "Int",
#             "width": 130,
#         },
#     ]


# def get_data(filters: dict | None = None) -> list[dict]:
#     # Replace this dummy data with real queries
#     return [
#         {
#             "date": "2025-05-01",
#             "branch_name": "Harare Main",
#             "amount": 10000,
#             "commission": 500,
#             "transaction_count": 50,
#         },
#         {
#             "date": "2025-05-01",
#             "branch_name": "Bulawayo Branch",
#             "amount": 8000,
#             "commission": 400,
#             "transaction_count": 40,
#         },
#     ]


# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from datetime import datetime

def execute(filters: dict | None = None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns() -> list[dict]:
    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Pay-in Branch"),
            "fieldname": "created_branch",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Destination Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Commission Paid"),
            "fieldname": "commission",
            "fieldtype": "Currency",
            "width": 130,
        },
        {
            "label": _("No. of Transactions"),
            "fieldname": "transaction_count",
            "fieldtype": "Int",
            "width": 130,
        },
    ]

def get_data(filters: dict | None = None) -> list[dict]:
    conditions = []
    parameters = {}

    # Validate filters
    if filters:
        if filters.get("start_date"):
            conditions.append("creation >= %(start_date)s")
            parameters["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            conditions.append("creation <= %(end_date)s")
            parameters["end_date"] = filters["end_date"]
        if filters.get("branch"):
            conditions.append("created_branch = %(branch)s")
            parameters["branch"] = filters["branch"]
        if filters.get("teller"):
            conditions.append("teller = %(teller)s")
            parameters["teller"] = filters["teller"]

    # Combine conditions
    conditions_str = " AND ".join(conditions)

    # Construct SQL query
    query = f"""
        SELECT
            DATE(creation) AS date,
            created_branch,
            SUM(receiver_amount) AS amount,
            SUM(charge) AS commission,
            COUNT(*) AS transaction_count
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 AND cash_in = 1 {('AND ' + conditions_str) if conditions_str else ''}
        GROUP BY
            DATE(creation), created_branch
        ORDER BY
            date, created_branch
    """

    # Fetch data from database
    data = frappe.db.sql(query, parameters, as_dict=True)
    return data
