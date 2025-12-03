# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Till"), "fieldname": "till", "fieldtype": "Link", "options": "Till", "width": 120},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Teller"), "fieldname": "teller", "fieldtype": "Link", "options": "Teller", "width": 120},
        {"label": _("Reference"), "fieldname": "name", "fieldtype": "Data", "width": 130},
        {"label": _("Status"), "fieldname": "transaction_status", "fieldtype": "Data", "width": 100},
        {"label": _("Cash In"), "fieldname": "cash_in_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Cash Out"), "fieldname": "cash_out_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Charge"), "fieldname": "charge", "fieldtype": "Currency", "width": 100},
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    data = []
    till_totals = {}

    # Get all transactions for the branch
    transactions = frappe.db.sql(f"""
        SELECT 
            CASE 
                WHEN cash_out = 1 THEN withdrawn_till
                WHEN cash_in = 1 THEN created_till
            END as till,
            posting_date,
            CASE 
                WHEN cash_out = 1 THEN withdrawn_by
                WHEN cash_in = 1 THEN owner
            END as teller,
            name,
            amount,
            receiver_amount,
            CASE 
                WHEN cash_in = 1 THEN charge
                ELSE NULL
            END as charge,
            transaction_status,
            cash_in,
            cash_out
        FROM 
            `tabTransaction`
        WHERE 
            docstatus = 1 AND (transaction_status = 'Completed' OR transaction_status = 'Reversed')
            AND (withdrawn_branch = %(branch)s OR created_branch = %(branch)s)
            {conditions}
        ORDER BY 
            till, posting_date
    """, filters, as_dict=1)

    # Process transactions and calculate totals
    for transaction in transactions:
        till = transaction.till
        if till not in till_totals:
            till_totals[till] = {
                'cash_in_total': 0,
                'cash_out_total': 0,
                'charge_total': 0
            }

        cash_in_amount = flt(transaction.amount) if transaction.cash_in else 0
        cash_out_amount = flt(transaction.receiver_amount) if transaction.cash_out else 0
        charge = flt(transaction.charge) if transaction.charge else 0  # Already filtered in SQL

        # Add to till totals
        till_totals[till]['cash_in_total'] += cash_in_amount
        till_totals[till]['cash_out_total'] += cash_out_amount
        till_totals[till]['charge_total'] += charge

        # Add transaction row
        data.append({
            'till': till,
            'posting_date': transaction.posting_date,
            'teller': transaction.teller,
            'name': transaction.name,
            'cash_in_amount': cash_in_amount,
            'cash_out_amount': cash_out_amount,
            'charge': transaction.charge,  # Will be NULL for cash-out
            'transaction_status': transaction.transaction_status, 
            'is_group': 0
        })

    # Add subtotal rows for each till
    grand_total_cash_in = 0
    grand_total_cash_out = 0
    grand_total_charge = 0

    for till, totals in till_totals.items():
        grand_total_cash_in += totals['cash_in_total']
        grand_total_cash_out += totals['cash_out_total']
        grand_total_charge += totals['charge_total']

        # Add subtotal row
        data.append({
            'till': "",
            'posting_date': '',
            'teller': _("Subtotal"),
            'name': '',
            'cash_in_amount': totals['cash_in_total'],
            'cash_out_amount': totals['cash_out_total'],
            'charge': totals['charge_total'],
            'transaction_status': '',
            'is_group': 1,
            'indent': 0
        })

    # Add grand total row
    if till_totals:
        data.append({
            'till': _("GRAND TOTAL"),
            'posting_date': '',
            'teller': '',
            'name': '',
            'cash_in_amount': grand_total_cash_in,
            'cash_out_amount': grand_total_cash_out,
            'charge': grand_total_charge,
            'transaction_type': '',
            'is_group': 1,
            'bold': 1
        })

    return data

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
    if filters.get("till"):
        conditions += " AND (withdrawn_till = %(till)s OR created_till = %(till)s)"
    return conditions