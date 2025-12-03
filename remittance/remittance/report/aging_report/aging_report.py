from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, flt
from frappe.utils.data import get_first_day, get_last_day

def execute(filters=None):
    filters = get_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    report_summary = get_report_summary(data)
    
    return columns, data, None, chart, report_summary

def get_filters(filters):
    if not filters:
        filters = {}
    
    # Set default date range to current month
    if not filters.get("from_date"):
        filters["from_date"] = get_first_day(nowdate())
    if not filters.get("to_date"):
        filters["to_date"] = nowdate()  # Use current date as default to_date
    
    # Ensure today date is always available for aging calculations
    filters["today"] = filters.get("to_date") or nowdate()
    
    return filters

def get_columns():
    return [
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Agent"),
            "fieldname": "agent",
            "fieldtype": "Link",
            "options": "Agent",
            "width": 120
        },
        {
            "label": _("Transaction ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Transaction",
            "width": 150
        },
        {
            "label": _("Sender Name"),
            "fieldname": "sender_name",
            "width": 180,
            "fieldtype": "Data"
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "width": 100,
            "fieldtype": "Data"
        },
        {
            "label": _("Days Outstanding"),
            "fieldname": "days_outstanding",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("0-7 Days"),
            "fieldname": "week1",
            "fieldtype": "Currency",
            "width": 120,
            "cell_color": "#90EE90"  # Light green
        },
        {
            "label": _("8-14 Days"),
            "fieldname": "week2",
            "fieldtype": "Currency",
            "width": 120,
            "cell_color": "#ADD8E6"  # Light blue
        },
        {
            "label": _("15-21 Days"),
            "fieldname": "week3",
            "fieldtype": "Currency",
            "width": 120,
            "cell_color": "#D3D3D3"  # Light grey
        },
        {
            "label": _("22+ Days"),
            "fieldname": "week4plus",
            "fieldtype": "Currency",
            "width": 120,
            "cell_color": "#FFCCCB"  # Light red
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            posting_date,
             
            name,
            sender_name,
            amount,
            transaction_status as status,
            DATEDIFF(%(today)s, posting_date) as days_outstanding
        FROM 
            `tabTransaction`
        WHERE 
            docstatus = 1
            AND transaction_status IN ('Pending', 'Pending Reversal')
            {conditions}
        ORDER BY 
            posting_date DESC
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=1)
    
    # Calculate aging buckets in Python for more control
    for row in data:
        days = row.get("days_outstanding", 0)
        amount = flt(row.get("amount", 0))
        
        # Initialize all buckets to 0
        row["week1"] = 0
        row["week2"] = 0
        row["week3"] = 0
        row["week4plus"] = 0
        
        # Assign amount to the correct bucket
        if days <= 7:
            row["week1"] = amount
        elif days <= 14:
            row["week2"] = amount
        elif days <= 21:
            row["week3"] = amount
        else:
            row["week4plus"] = amount
    
    return data

def get_conditions(filters):
    conditions = []
    
    # Date range filtering
    conditions.append("AND posting_date BETWEEN %(from_date)s AND %(to_date)s")
    
    # Agent filtering
    # if filters.get("agent"):
    #     conditions.append("AND agent = %(agent)s")
    
    # Sender name filtering
    if filters.get("sender_name"):
        conditions.append("AND sender_name LIKE %(sender_name)s")
        filters["sender_name"] = f"%{filters['sender_name']}%"
    
    # Amount range filtering
    if filters.get("min_amount"):
        conditions.append("AND amount >= %(min_amount)s")
    if filters.get("max_amount"):
        conditions.append("AND amount <= %(max_amount)s")
    
    # Age bucket filtering
    if filters.get("age_bucket"):
        if filters["age_bucket"] == "0-7":
            conditions.append("AND DATEDIFF(%(today)s, posting_date) <= 7")
        elif filters["age_bucket"] == "8-14":
            conditions.append("AND DATEDIFF(%(today)s, posting_date) BETWEEN 8 AND 14")
        elif filters["age_bucket"] == "15-21":
            conditions.append("AND DATEDIFF(%(today)s, posting_date) BETWEEN 15 AND 21")
        elif filters["age_bucket"] == "22+":
            conditions.append("AND DATEDIFF(%(today)s, posting_date) > 21")
    
    return " ".join(conditions) if conditions else ""

def get_report_summary(data):
    if not data:
        return None
        
    totals = {
        "total": 0,
        "week1": 0,
        "week2": 0,
        "week3": 0,
        "week4plus": 0
    }
    
    for row in data:
        totals["total"] += flt(row.get("amount", 0))
        totals["week1"] += flt(row.get("week1", 0))
        totals["week2"] += flt(row.get("week2", 0))
        totals["week3"] += flt(row.get("week3", 0))
        totals["week4plus"] += flt(row.get("week4plus", 0))
    
    return [
        {
            "value": totals["total"],
            "label": _("Total Outstanding"),
            "datatype": "Currency",
            "indicator": "Red" if totals["total"] > 0 else "Green"
        },
        {
            "value": totals["week1"],
            "label": _("0-7 Days"),
            "datatype": "Currency",
            "indicator": "Green"
        },
        {
            "value": totals["week2"],
            "label": _("8-14 Days"),
            "datatype": "Currency",
            "indicator": "Blue"
        },
        {
            "value": totals["week3"],
            "label": _("15-21 Days"),
            "datatype": "Currency",
            "indicator": "Gray"
        },
        {
            "value": totals["week4plus"],
            "label": _("22+ Days"),
            "datatype": "Currency",
            "indicator": "Red"
        }
    ]

def get_chart(data):
    if not data:
        return None
        
    totals = {
        "week1": 0,
        "week2": 0,
        "week3": 0,
        "week4plus": 0
    }
    
    for row in data:
        totals["week1"] += flt(row.get("week1", 0))
        totals["week2"] += flt(row.get("week2", 0))
        totals["week3"] += flt(row.get("week3", 0))
        totals["week4plus"] += flt(row.get("week4plus", 0))
    
    return {
        "data": {
            "labels": ["0-7 Days", "8-14 Days", "15-21 Days", "22+ Days"],
            "datasets": [{
                "name": "Outstanding Amount",
                "values": [
                    totals["week1"],
                    totals["week2"],
                    totals["week3"],
                    totals["week4plus"]
                ]
            }]
        },
        "type": "bar",
        "barOptions": {
            "stacked": False,
            "spaceRatio": 0.5
        },
        "colors": ["#90EE90", "#ADD8E6", "#D3D3D3", "#FFCCCB"],
        "height": 250,
        "axisOptions": {
            "xAxisMode": "tick",
            "yAxisMode": "tick"
        }
    }