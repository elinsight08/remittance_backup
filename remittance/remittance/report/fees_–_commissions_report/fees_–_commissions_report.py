# commission_charges_report.py
from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import getdate, nowdate

def execute(filters=None):
    filters = frappe._dict(filters or {})
    set_default_month_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    
    if data:
        grand_charges = sum(d.get("charges", 0) for d in data)
        grand_commissions = sum(d.get("commissions", 0) for d in data)
        
        grand_totals = {
            "date": "<b>Grand Total</b>",
            "charges": grand_charges,
            "commissions": grand_commissions,
            "total_charge_excl_commission": grand_charges - grand_commissions,
            "bold": 1
        }
        data.append(grand_totals)
    
    return columns, data

def set_default_month_filters(filters):
    today = getdate(nowdate())
    first_day = today.replace(day=1)
    last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    if not filters.get("from_date"):
        filters.from_date = first_day
    if not filters.get("to_date"):
        filters.to_date = last_day

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Data", "width": 120},
        {"label": _("Charges"), "fieldname": "charges", "fieldtype": "Currency", "width": 120},
        {"label": _("Commissions"), "fieldname": "commissions", "fieldtype": "Currency", "width": 120},
        {"label": _("Total Charge Excl Commission"), "fieldname": "total_charge_excl_commission", 
         "fieldtype": "Currency", "width": 240}
    ]

def get_data(filters):
    date_range = get_date_range(filters.from_date, filters.to_date)
    actual_data = get_actual_transaction_data(filters)
    
    results = []
    for date in date_range:
        date_str = date.strftime('%Y-%m-%d')
        
        row = {
            "date": date.strftime('%d-%m-%Y'),
            "charges": actual_data.get(date_str, {}).get("charges", 0),
            "commissions": actual_data.get(date_str, {}).get("commissions", 0)
        }
        row["total_charge_excl_commission"] = row["charges"] - row["commissions"]
        results.append(row)
    
    return results

def get_date_range(start_date, end_date):
    start = getdate(start_date)
    end = getdate(end_date)
    
    date_range = []
    current = start
    while current <= end:
        date_range.append(current)
        current += timedelta(days=1)
    return date_range

def get_actual_transaction_data(filters):
    data = {}
    
    # Get charges
    charges_query = """
        SELECT 
            DATE(posting_date) as date,
            SUM(charge) as charges
        FROM `tabTransaction`
        WHERE docstatus = 1
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        {additional_conditions}
        GROUP BY DATE(posting_date)
    """.format(additional_conditions=get_additional_conditions(filters))
    
    # Get commissions
    commissions_query = """
        SELECT 
            DATE(posting_date) as date,
            SUM(amount) as commissions
        FROM `tabCommission Transaction`
        WHERE is_paid = 0 
        AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        {additional_conditions}
        GROUP BY DATE(posting_date)
    """.format(additional_conditions=get_additional_conditions(filters))
    
    # Execute queries
    for row in frappe.db.sql(charges_query, filters, as_dict=1):
        data.setdefault(row['date'].strftime('%Y-%m-%d'), {"charges": 0, "commissions": 0})
        data[row['date'].strftime('%Y-%m-%d')]["charges"] = row["charges"] or 0
    
    for row in frappe.db.sql(commissions_query, filters, as_dict=1):
        data.setdefault(row['date'].strftime('%Y-%m-%d'), {"charges": 0, "commissions": 0})
        data[row['date'].strftime('%Y-%m-%d')]["commissions"] = row["commissions"] or 0
    
    return data

def get_additional_conditions(filters):
    conditions = []
    if filters.get("agent"):
        conditions.append("AND agent = %(agent)s")
    return " ".join(conditions)