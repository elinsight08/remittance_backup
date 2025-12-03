# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class Till(Document):
    
	def before_insert(self):
		# check if self.select_till has been assigned to another Teller
		user = frappe.session.user
		user_doc = frappe.get_doc("User", user)
		if user_doc.is_agent:
			self.company = user_doc.agent # agent == company


@frappe.whitelist()
def close_till(docname):
    print("Docname.........................", docname)
    till_ob = frappe.get_doc("Till", docname)
    till_ob.enabled = 0
    # till_ob.opening_balance =0.0
    till_ob.save()
    
@frappe.whitelist()
def open_till(docname):
    today_date = today()
    till_ob = frappe.get_doc("Till", docname)
    # current_balance = 0.0
    update_float = False
    recon = frappe.get_all("Till Reconciliation", filters={
        "till": docname,
        "posting_date": today_date,
    }, fields=["name", "docstatus"], limit=1)
    if recon:
        recon_doc = frappe.get_doc("Till Reconciliation", recon[0].name)
        print("recon_doc............", recon_doc)
        if recon_doc.docstatus in [1, 0]:
            # recon_doc.cancel()
            # current_balance = recon_doc.closing_float
            update_float = True
        else:
            pass
            
    till_ob.enabled = 1
    if update_float:
        # till_ob.current_balance = current_balance 
        # till_ob.cash_in_hand = till_ob.closing_balance - current_balance # current_balance is closing balance
        # till_ob.closing_balance = 0.0
        pass
    till_ob.save()
 
 