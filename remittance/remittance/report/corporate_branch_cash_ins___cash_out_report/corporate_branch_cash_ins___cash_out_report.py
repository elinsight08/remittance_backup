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
        {"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 150},
        {"label": _("Till"), "fieldname": "till", "fieldtype": "Link", "options": "Till", "width": 120},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Cash In"), "fieldname": "cash_in_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Cash Out"), "fieldname": "cash_out_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Charge"), "fieldname": "charge", "fieldtype": "Currency", "width": 100},
        {"label": _("Net Movement"), "fieldname": "net_movement", "fieldtype": "Currency", "width": 120}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    data = []
    branch_totals = {}

    # Get all transactions across branches
    transactions = frappe.db.sql(f"""
        SELECT 
            CASE 
                WHEN cash_out = 1 THEN withdrawn_branch
                WHEN cash_in = 1 THEN created_branch
            END as branch,
            CASE 
                WHEN cash_out = 1 THEN withdrawn_till
                WHEN cash_in = 1 THEN created_till
            END as till,
            posting_date,
            name,
            CASE 
                WHEN cash_in = 1 THEN amount
                ELSE 0
            END as cash_in_amount,
            CASE 
                WHEN cash_out = 1 THEN receiver_amount
                ELSE 0
            END as cash_out_amount,
            CASE 
                WHEN cash_in = 1 THEN charge
                ELSE 0
            END as charge
        FROM 
            `tabTransaction`
        WHERE 
           docstatus = 1 AND (transaction_status = 'Completed' OR transaction_status = 'Reversed')
            AND (withdrawn_branch = %(branch)s OR created_branch = %(branch)s)
            {conditions}
        ORDER BY 
            branch, till, posting_date
    """, filters, as_dict=1)

    # Process transactions and calculate totals
    for transaction in transactions:
        branch = transaction.branch
        till = transaction.till
        
        if branch not in branch_totals:
            branch_totals[branch] = {
                'cash_in_total': 0,
                'cash_out_total': 0,
                'charge_total': 0,
                'tills': {}
            }
        
        if till not in branch_totals[branch]['tills']:
            branch_totals[branch]['tills'][till] = {
                'cash_in_total': 0,
                'cash_out_total': 0,
                'charge_total': 0
            }

        cash_in = flt(transaction.cash_in_amount)
        cash_out = flt(transaction.cash_out_amount)
        charge = flt(transaction.charge)
        net_movement = cash_in - cash_out

        # Add to branch totals
        branch_totals[branch]['cash_in_total'] += cash_in
        branch_totals[branch]['cash_out_total'] += cash_out
        branch_totals[branch]['charge_total'] += charge
        
        # Add to till totals
        branch_totals[branch]['tills'][till]['cash_in_total'] += cash_in
        branch_totals[branch]['tills'][till]['cash_out_total'] += cash_out
        branch_totals[branch]['tills'][till]['charge_total'] += charge

        # Add transaction row
        data.append({
            'branch': branch,
            'till': till,
            'posting_date': transaction.posting_date,
            'cash_in_amount': cash_in,
            'cash_out_amount': cash_out,
            'charge': charge,
            'net_movement': net_movement,
            'is_group': 0
        })

    # Add branch summary rows
    corporate_totals = {
        'cash_in_total': 0,
        'cash_out_total': 0,
        'charge_total': 0,
        'net_movement_total': 0
    }

    for branch, totals in branch_totals.items():
        # Add till subtotals for each branch
        for till, till_totals in totals['tills'].items():
            net_movement = till_totals['cash_in_total'] - till_totals['cash_out_total']
            data.append({
                'branch': branch,
                'till': till,
                'posting_date': _("Till Subtotal"),
                'cash_in_amount': till_totals['cash_in_total'],
                'cash_out_amount': till_totals['cash_out_total'],
                'charge': till_totals['charge_total'],
                'net_movement': net_movement,
                'is_group': 1,
                'indent': 1
            })

        # Add branch totals
        branch_net = totals['cash_in_total'] - totals['cash_out_total']
        data.append({
            'branch': branch,
            'till': _("Branch Total"),
            'posting_date': '',
            'cash_in_amount': totals['cash_in_total'],
            'cash_out_amount': totals['cash_out_total'],
            'charge': totals['charge_total'],
            'net_movement': branch_net,
            'is_group': 1,
            'bold': 1,
            'indent': 0
        })

        # Add to corporate totals
        corporate_totals['cash_in_total'] += totals['cash_in_total']
        corporate_totals['cash_out_total'] += totals['cash_out_total']
        corporate_totals['charge_total'] += totals['charge_total']
        corporate_totals['net_movement_total'] += branch_net

    # Add corporate totals
    data.append({
        'branch': _("CORPORATE TOTAL"),
        'till': '',
        'posting_date': '',
        'cash_in_amount': corporate_totals['cash_in_total'],
        'cash_out_amount': corporate_totals['cash_out_total'],
        'charge': corporate_totals['charge_total'],
        'net_movement': corporate_totals['net_movement_total'],
        'is_group': 1,
        'bold': 1,
        'indent': 0
    })

    return data

def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
    if filters.get("branch"):
        conditions.append("(withdrawn_branch = %(branch)s OR created_branch = %(branch)s)")
    if filters.get("till"):
        conditions.append("(withdrawn_till = %(till)s OR created_till = %(till)s)")
    
    return " AND " + " AND ".join(conditions) if conditions else ""