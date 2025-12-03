# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
    """Return columns and data for the report.
    
    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns() -> list[dict]:
    """Return columns for the report."""
    return [
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 80},
        {"label": _("Total Pay-ins"), "fieldname": "total_payins", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Pay-outs"), "fieldname": "total_payouts", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Commissions"), "fieldname": "total_commissions", "fieldtype": "Currency", "width": 120},
    ]

def get_data(filters) -> list[dict]:
    """Fetch and return report data based on filters."""
    
    conditions = []
    parameters = {}

    # Validate filters and construct conditions
    if filters:
        if filters.get("start_date"):
            conditions.append("creation >= %(start_date)s")
            parameters["start_date"] = filters["start_date"]
        if filters.get("end_date"):
            conditions.append("creation <= %(end_date)s")
            parameters["end_date"] = filters["end_date"]

    # Combine conditions into a single string
    conditions_str = " AND ".join(conditions)

    # Construct the SQL query for aggregation
    query = f"""
        SELECT
            currency,
            SUM(CASE WHEN cash_in = 1 THEN amount ELSE 0 END) AS total_payins,
            SUM(CASE WHEN cash_out = 1 THEN receiver_amount ELSE 0 END) AS total_payouts,
            SUM(charge) AS total_commissions
        FROM
            `tabTransaction`
        WHERE
            docstatus = 1 {('AND ' + conditions_str) if conditions_str else ''}
        GROUP BY
            currency
    """

    # Execute the query and fetch results
    data = frappe.db.sql(query, parameters, as_dict=True)

    return data