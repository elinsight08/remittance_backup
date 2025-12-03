# agent_commission_report.py
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate, flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    data = add_totals(data)
    return columns, data

def get_columns():
    return [
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Agent"), "fieldname": "agent", "fieldtype": "Link", "options": "Agent", "width": 120},
        {"label": _("Transaction"), "fieldname": "transaction", "fieldtype": "Link", "options": "Transaction", "width": 150},
        {"label": _("Sender Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 220},
        {"label": _("Receiver Amount"), "fieldname": "receiver_amount", "fieldtype": "Currency", "width": 220},
        {"label": _("Charge"), "fieldname": "charge", "fieldtype": "Currency", "width": 120},
        {"label": _("Commission"), "fieldname": "commission", "fieldtype": "Currency", "width": 120}
    ]

def get_data(filters):
    commission_query = """
        SELECT 
            ct.posting_date,
            ct.agent,
            ct.ref_doc as transaction,
            ct.amount as commission,
            t.amount,
            t.charge,
            t.receiver_amount,
            t.name as transaction_name
        FROM `tabCommission Transaction` ct
        JOIN `tabTransaction` t ON ct.ref_doc = t.name
        WHERE t.docstatus = 1
        {conditions}
        ORDER BY ct.agent, ct.posting_date
    """.format(conditions=get_conditions(filters))
    
    data = frappe.db.sql(commission_query, filters, as_dict=1)
    
    for row in data:
        row['transaction'] = row.get('transaction_name')
        # Calculate receiver amount if not directly available
        if 'receiver_amount' not in row:
            row['receiver_amount'] = flt(row.get('amount', 0)) - flt(row.get('charge', 0)) - flt(row.get('commission', 0))
    
    return data

def add_totals(data):
    if not data:
        return []
    
    sorted_data = sorted(data, key=lambda x: (x['agent'], x['posting_date']))
    grouped_data = []
    current_agent = None
    agent_subtotal = {
        'amount': 0, 
        'receiver_amount': 0,
        'charge': 0, 
        'commission': 0
    }
    
    for row in sorted_data:
        if current_agent and current_agent != row['agent']:
            # Add subtotal row for previous agent
            grouped_data.append({
                'posting_date': '',
                'agent': current_agent,
                'transaction': _("<b>Subtotal</b>"),
                'amount': agent_subtotal['amount'],
                'receiver_amount': agent_subtotal['receiver_amount'],
                'charge': agent_subtotal['charge'],
                'commission': agent_subtotal['commission'],
                'indent': 0,
                'bold': 1,
                'is_subtotal': True
            })
            agent_subtotal = {
                'amount': 0,
                'receiver_amount': 0,
                'charge': 0,
                'commission': 0
            }
        
        current_agent = row['agent']
        agent_subtotal['amount'] += flt(row.get('amount', 0))
        agent_subtotal['receiver_amount'] += flt(row.get('receiver_amount', 0))
        agent_subtotal['charge'] += flt(row.get('charge', 0))
        agent_subtotal['commission'] += flt(row.get('commission', 0))
        
        grouped_data.append(row)
    
    # Add final agent subtotal if there was any data
    if current_agent:
        grouped_data.append({
            'posting_date': '',
            'agent':  "",
            'transaction': _("Subtotal"),
            'amount': agent_subtotal['amount'],
            'receiver_amount': agent_subtotal['receiver_amount'],
            'charge': agent_subtotal['charge'],
            'commission': agent_subtotal['commission'],
            'indent': 0,
            'bold': 1,
            'is_subtotal': True
        })
    
    # Calculate grand totals from subtotals only
    grand_total = {
        'amount': 0,
        'receiver_amount': 0,
        'charge': 0,
        'commission': 0
    }
    
    for row in grouped_data:
        if row.get('is_subtotal'):
            grand_total['amount'] += flt(row.get('amount', 0))
            grand_total['receiver_amount'] += flt(row.get('receiver_amount', 0))
            grand_total['charge'] += flt(row.get('charge', 0))
            grand_total['commission'] += flt(row.get('commission', 0))
    
    # Add grand total row
    grouped_data.append({
        'posting_date': '',
        'agent':  _("Grand Total"),
        'transaction':'',
        'amount': grand_total['amount'],
        'receiver_amount': grand_total['receiver_amount'],
        'charge': grand_total['charge'],
        'commission': grand_total['commission'],
        'indent': 0,
        'bold': 1,
        'is_grand_total': True
    })
    
    return grouped_data

def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("AND ct.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("AND ct.posting_date <= %(to_date)s")
    if filters.get("agent"):
        conditions.append("AND ct.agent = %(agent)s")
    return " ".join(conditions) if conditions else ""