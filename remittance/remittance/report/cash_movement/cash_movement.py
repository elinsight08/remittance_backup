import frappe
from frappe import _
from frappe.utils import getdate, flt

def execute(filters=None):
    """Main function to generate the Float Allocation Report"""
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    # chart = get_chart_data(data, filters)
    # report_summary = get_report_summary(data, filters)

    return columns, data, None #, chart , report_summary

def get_columns():
    """Define report columns"""
    return [
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Float ID"),
            "fieldname": "float_allocation",
            "fieldtype": "Link",
            "options": "Float Allocation",
            "width": 120
        },
        {
            "label": _("Status"),
            "fieldname": "docstatus",
            "fieldtype": "Select",
            "width": 80,
            "options": "Draft\nSubmitted\nCancelled"
        },
        {
            "label": _("Source Type"),
            "fieldname": "source_type",
            "fieldtype": "Select",
            "width": 100,
            "options": "Branch\nTill\nAgent"
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "fieldtype": "Dynamic Link",
            "options": "source_type",
            "width": 150
        },
        {
            "label": _("Destination Type"),
            "fieldname": "destination_type",
            "fieldtype": "Select",
            "width": 120,
            "options": "Branch\nTill\nAgent"
        },
        {
            "label": _("Destination"),
            "fieldname": "destination",
            "fieldtype": "Dynamic Link",
            "options": "destination_type",
            "width": 150
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120,
            "options": "currency"
        },
        {
            "label": _("Currency"),
            "fieldname": "currency",
            "fieldtype": "Link",
            "options": "Currency",
            "width": 80
        },
        {
            "label": _("Company"),
            "fieldname": "company",
            "fieldtype": "Link",
            "options": "Company",
            "width": 120
        },
        {
            "label": _("Default Branch"),
            "fieldname": "default_branch",
            "fieldtype": "Link",
            "options": "Branch",
            "width": 120
        }
    ]

def get_data(filters):
    """Get report data based on filters"""
    conditions, values = get_conditions(filters)

    query = """
        SELECT
            fa.name as float_allocation,
            fa.posting_date,
            fa.docstatus,
            fa.source_type,
            CASE
                WHEN fa.source_type = 'Branch' THEN fa.from_branch
                WHEN fa.source_type = 'Till' THEN fa.from_till
                WHEN fa.source_type = 'Agent' THEN fa.from_agent
            END as source,
            fa.destination_type,
            CASE
                WHEN fa.destination_type = 'Branch' THEN fa.to_branch
                WHEN fa.destination_type = 'Till' THEN fa.to_till
                WHEN fa.destination_type = 'Agent' THEN fa.to_agent
            END as destination,
            fa.amount,
            fa.currency,
            fa.company,
            fa.default_branch,
            fa.amended_from
        FROM `tabFloat Allocation` fa
        WHERE 1=1
        {conditions}
        ORDER BY fa.posting_date ASC, fa.creation ASC
    """.format(conditions=conditions)

    data = frappe.db.sql(query, values, as_dict=1)

    # Format the data
    for row in data:
        # Convert docstatus to meaningful status
        if row.docstatus == 0:
            row['docstatus'] = 'Draft'
        elif row.docstatus == 1:
            row['docstatus'] = 'Submitted'
        elif row.docstatus == 2:
            row['docstatus'] = 'Cancelled'

        # Add source and destination names if needed
        row = add_display_names(row)

    return data

def get_conditions(filters):
    """Build conditions based on filters"""
    conditions = []
    values = {}

    if filters.get("company"):
        conditions.append("fa.company = %(company)s")
        values["company"] = filters.get("company")

    if filters.get("from_date"):
        conditions.append("fa.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("fa.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    if filters.get("source_type"):
        conditions.append("fa.source_type = %(source_type)s")
        values["source_type"] = filters.get("source_type")

    if filters.get("destination_type"):
        conditions.append("fa.destination_type = %(destination_type)s")
        values["destination_type"] = filters.get("destination_type")

    if filters.get("default_branch"):
        conditions.append("fa.default_branch = %(default_branch)s")
        values["default_branch"] = filters.get("default_branch")

    if filters.get("currency"):
        conditions.append("fa.currency = %(currency)s")
        values["currency"] = filters.get("currency")

    if filters.get("status"):
        status_map = {
            "Draft": 0,
            "Submitted": 1,
            "Cancelled": 2
        }
        if filters.get("status") in status_map:
            conditions.append("fa.docstatus = %(docstatus)s")
            values["docstatus"] = status_map[filters.get("status")]

    # Filter by source (dynamic based on source_type)
    if filters.get("source"):
        source_type = filters.get("source_type")
        if source_type == 'Branch':
            conditions.append("fa.from_branch = %(source)s")
            values["source"] = filters.get("source")
        elif source_type == 'Till':
            conditions.append("fa.from_till = %(source)s")
            values["source"] = filters.get("source")
        elif source_type == 'Agent':
            conditions.append("fa.from_agent = %(source)s")
            values["source"] = filters.get("source")

    # Filter by destination (dynamic based on destination_type)
    if filters.get("destination"):
        dest_type = filters.get("destination_type")
        if dest_type == 'Branch':
            conditions.append("fa.to_branch = %(destination)s")
            values["destination"] = filters.get("destination")
        elif dest_type == 'Till':
            conditions.append("fa.to_till = %(destination)s")
            values["destination"] = filters.get("destination")
        elif dest_type == 'Agent':
            conditions.append("fa.to_agent = %(destination)s")
            values["destination"] = filters.get("destination")

    # If no status filter, exclude cancelled by default
    if not filters.get("status"):
        conditions.append("fa.docstatus != 2")

    return " AND " + " AND ".join(conditions) if conditions else "", values

def add_display_names(row):
    """Add display names for linked documents"""
    try:
        # Get source display name
        if row.get('source') and row.get('source_type'):
            if row['source_type'] == 'Branch':
                row['source_display'] = frappe.db.get_value('Branch', row['source'], 'branch_name') or row['source']
            elif row['source_type'] == 'Till':
                row['source_display'] = frappe.db.get_value('Till', row['source'], 'till_name') or row['source']
            elif row['source_type'] == 'Agent':
                row['source_display'] = frappe.db.get_value('Agent', row['source'], 'agent_name') or row['source']

        # Get destination display name
        if row.get('destination') and row.get('destination_type'):
            if row['destination_type'] == 'Branch':
                row['destination_display'] = frappe.db.get_value('Branch', row['destination'], 'branch_name') or row['destination']
            elif row['destination_type'] == 'Till':
                row['destination_display'] = frappe.db.get_value('Till', row['destination'], 'till_name') or row['destination']
            elif row['destination_type'] == 'Agent':
                row['destination_display'] = frappe.db.get_value('Agent', row['destination'], 'agent_name') or row['destination']

    except Exception:
        # If there's any error getting display names, use the ID
        pass

    return row

# def get_chart_data(data, filters):
#     """Generate chart data for the report"""
#     if not data:
#         return None

#     # Chart 1: Amount by Source Type
#     source_type_data = {}
#     for row in data:
#         if row.get('docstatus') == 'Cancelled':
#             continue

#         source_type = row.get('source_type', 'Unknown')
#         amount = flt(row.get('amount', 0))

#         if source_type in source_type_data:
#             source_type_data[source_type] += amount
#         else:
#             source_type_data[source_type] = amount

#     if source_type_data:
#         chart_data = {
#             "data": {
#                 "labels": list(source_type_data.keys()),
#                 "datasets": [{
#                     "name": _("Amount by Source Type"),
#                     "values": list(source_type_data.values())
#                 }]
#             },
#             "type": "donut",
#             "title": _("Float Allocation by Source Type")
#         }
#         return chart_data

#     return None

# def get_report_summary(data, filters):
#     """Generate report summary"""
#     if not data:
#         return []

#     total_amount = 0
#     draft_count = 0
#     submitted_count = 0
#     cancelled_count = 0

#     for row in data:
#         amount = flt(row.get('amount', 0))
#         status = row.get('docstatus')

#         if status == 'Draft':
#             draft_count += 1
#         elif status == 'Submitted':
#             submitted_count += 1
#             total_amount += amount
#         elif status == 'Cancelled':
#             cancelled_count += 1

#     currency = data[0].get('currency') if data else frappe.db.get_single_value('Global Defaults', 'default_currency')

#     return [
#         {
#             "value": total_amount,
#             "indicator": "Green" if total_amount > 0 else "Gray",
#             "label": _("Total Allocated Amount"),
#             "datatype": "Currency",
#             "currency": currency
#         },
#         {
#             "value": submitted_count,
#             "indicator": "Blue",
#             "label": _("Submitted Allocations"),
#             "datatype": "Int"
#         },
#         {
#             "value": draft_count,
#             "indicator": "Orange",
#             "label": _("Draft Allocations"),
#             "datatype": "Int"
#         },
#         {
#             "value": cancelled_count,
#             "indicator": "Red",
#             "label": _("Cancelled Allocations"),
#             "datatype": "Int"
#         }
#     ]
