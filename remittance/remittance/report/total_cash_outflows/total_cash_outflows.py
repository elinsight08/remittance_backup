# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

# import frappe
from frappe import _


def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_data()

    return columns, data


def get_columns() -> list[dict]:
    """Return columns for the report.

    One field definition per column, just like a DocType field definition.
    """
    return [
        {
            "label": _("Transaction ID"),
            "fieldname": "transaction_id",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Date"),
            "fieldname": "transaction_date",
            "fieldtype": "Datetime",
            "width": 150,
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "fieldtype": "Data",
            "width": 150,
            "description": "Source of the cash (Teller till, Branch vault, Corporate till)",
        },
        {
            "label": _("Destination"),
            "fieldname": "destination",
            "fieldtype": "Data",
            "width": 150,
            "description": "Destination of cash (Another teller, branch vault, HQ/Corporate vault)",
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Currency"),
            "fieldname": "currency",
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "label": _("Transaction Type"),
            "fieldname": "transaction_type",
            "fieldtype": "Data",
            "width": 120,
            "description": "Pay-out or Float Out",
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 200,
        },
    ]


def get_data() -> list[list]:
    """Return data for the report.

    The report data is a list of rows, with each row being a list of cell values.
    """
    # Dummy data - replace with your database query logic
    return [
        [
            "TXN-1001",
            "2025-05-28 10:15:00",
            "Teller Till 01",
            "Branch Vault 02",
            5000.00,
            "USD",
            "Pay-out",
            "Cash payout to branch vault"
        ],
        [
            "TXN-1002",
            "2025-05-28 11:00:00",
            "Branch Vault 02",
            "Teller Till 01",
            2000.00,
            "USD",
            "Float Out",
            "Cash float to teller"
        ],
    ]
