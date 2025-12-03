# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


def execute(filters: dict | None = None):
    """Return columns and data for the report."""
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns() -> list[dict]:
    """Return columns for the Agents report.

    Follows pay-ins/pay-outs structure plus agent commission.
    """
    return [
        {
            "label": _("Date"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Agent Name"),
            "fieldname": "agent_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Branch Name"),
            "fieldname": "branch_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Transaction Type"),
            "fieldname": "transaction_type",
            "fieldtype": "Data",
            "width": 100,
            # Could be "Pay-in", "Pay-out", "Uncollected", "Reversal"
        },
        {
            "label": _("Transaction Amount"),
            "fieldname": "transaction_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Agent Commission Earned"),
            "fieldname": "agent_commission",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 200,
        },
    ]


def get_data() -> list[list]:
    """Return data rows for the report.

    This is a placeholder. Replace it with actual query or data fetching logic.
    """
    return [
        [
            "2025-05-01",
            "Agent John",
            "Central Branch",
            "Pay-in",
            1000.00,
            50.00,
            "Completed",
            "No issues",
        ],
        [
            "2025-05-02",
            "Agent Mary",
            "West Branch",
            "Pay-out",
            500.00,
            25.00,
            "Completed",
            "",
        ],
    ]
