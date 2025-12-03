import frappe
from frappe.utils import nowdate

def update_opening_balance_for_tills():
    tills = frappe.get_all("Till", fields=["name", "closing_balance", "opening_balance", "cash_in_hand", "current_balance"])

    for till in tills:
        if till:
            # opening_balance = till.cash_in_hand + till.current_balance
            frappe.db.set_value("Till", till.name, {
                # "opening_balance": opening_balance,
                "cash_in_hand": 0.00,
                "enabled": 1,
                # "closing_balance":0.00
            })
            pass

    frappe.db.commit()
    frappe.logger().info(f"[{nowdate()}] Opening balances updated and tills enabled for {len(tills)} tills.")
