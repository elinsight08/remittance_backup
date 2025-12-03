import frappe

@frappe.whitelist()
def get_cashout_trans(search_text=None, limit=20):
    """
    Get transactions filtered by exact name with specific document and transaction statuses.
    """
    # Base SQL query
    query = """
        SELECT name, receiver_id, mobile_no, receiver_name, sender_name, currency, receiver_amount, transaction_status, modified
        FROM `tabTransaction`
        WHERE 1=1
    """
    conditions = []
    params = []

    if not search_text or not search_text.strip():
        return []
    else:
        # Exact match for name and status checks
        conditions.append("name = %s")
        params.append(search_text)  # Exact match for name
        conditions.append("docstatus = 1 AND (transaction_status = 'Pending' OR transaction_status = 'Pending Reversal')")

        if conditions:
            query += " AND " + " AND ".join(conditions)

    # Order by modified date and add limit
    query += " ORDER BY modified DESC LIMIT %s"
    params.append(limit)

    # Execute the query
    results = frappe.db.sql(query, params, as_dict=True)

    return results

        # conditions.append("(name LIKE %s OR receiver_id LIKE %s OR mobile_no LIKE %s OR receiver_name LIKE %s )")
