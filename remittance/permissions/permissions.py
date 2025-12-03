# import frappe

# def transaction_permission_query(user):
#     if not user:
#         user = frappe.session.user
        
#     if "System Manager" in frappe.get_roles(user):
#         return ""  # Admins see all records
#     else:
#         return f"`tabTransaction`.owner = {frappe.db.escape(user)}"


import frappe
from frappe.utils import nowdate

def transaction_permission_query(user):
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return ""

    escaped_user = frappe.db.escape(user)
    today = nowdate()
    escaped_today = frappe.db.escape(today)

    # For Till Operator
    if "Till Operator" in frappe.get_roles(user):
        return (
            f"docstatus = 1 AND DATE(`tabTransaction`.modified) = {escaped_today} "
            f"AND (`tabTransaction`.owner = {escaped_user} OR `tabTransaction`.withdrawn_by = {escaped_user})"
        )

    # Fallback: allow only owned or modified today
    return (
        f"(`tabTransaction`.owner = {escaped_user} "
        f"OR DATE(`tabTransaction`.modified) = {escaped_today})"
    )
