import frappe

def is_till_active():
    print("Checking..............")
    role = "Till Operator"
    user = frappe.session.user

    # Check if user has the role
    if role in frappe.get_roles(user):
        # Fetch the till associated with the user
        till = frappe.get_doc("Till", {"operator": user})

        # Check if the till is enabled
        if till.enabled:
            pass
            # return True
    return False

