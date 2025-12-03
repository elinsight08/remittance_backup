import frappe
from frappe.utils import today

@frappe.whitelist()
def get_balance():
    print("Loading...................")
    user = frappe.get_doc("User", frappe.session.user)
    teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])
    float_balance = 0
    total_received = 0
    total_sent = 0
    cash_balance = 0.00
    if frappe.session.user != "Administrator":
        if user.is_agent:
            if teller:
                till_name = teller[0].select_till
                print("Till ......", till_name)
                if till_name:
                    till_object = frappe.get_doc("Till", till_name)
                    if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                    float_balance = till_object.current_balance
                    transactions = frappe.get_all("Transaction",
												filters={"owner": user.email,
														"posting_date":frappe.utils.now(),
														"cash_in": 1,
                                                        "docstatus": 1
														}, fields=["amount"])
                    total_received = sum(t["amount"] for t in transactions)
                    transactions_two = frappe.get_all("Transaction",
												filters={"withdrawn_by": user.email,
														"withdrawal_date":frappe.utils.now(),
														"cash_out": 1,
                                                        "docstatus": 1
														}, fields=["receiver_amount"])
                    total_sent = sum(t["receiver_amount"] for t in transactions_two)
                    cash_balance = till_object.current_balance
                else:
                    agent_object = frappe.get_doc("Agent", user.agent)
                    float_balance = agent_object.current_balance
                    transactions = frappe.get_all("Transaction",
												filters={"owner": user.email,
														"posting_date":frappe.utils.now(),
														"cash_in": 1,
                                                        "docstatus": 1
														}, fields=["amount"])
                    total_received = sum(t["amount"] for t in transactions)
                    transactions_two = frappe.get_all("Transaction",
												filters={"withdrawn_by": user.email,
														"withdrawal_date":frappe.utils.now(),
														"cash_out": 1,
                                                        "docstatus": 1
														}, fields=["receiver_amount"])
                    total_sent = sum(t["receiver_amount"] for t in transactions_two)
                    cash_balance = agent_object.current_balance
            else:
                agent_object = frappe.get_doc("Agent", user.agent)
                float_balance = agent_object.current_balance
                transactions = frappe.get_all("Transaction",
                                              filters={"owner": user.email,
                                                       "posting_date":frappe.utils.now(),
                                                       "cash_in": 1,
                                                        "docstatus": 1
                                                       }, fields=["amount"])
                total_received = sum(t["amount"] for t in transactions)
                transactions_two = frappe.get_all("Transaction",
                                              filters={"withdrawn_by": user.email,
                                                       "withdrawal_date":frappe.utils.now(),
                                                       "cash_out": 1,
                                                       "docstatus": 1
                                                       }, fields=["receiver_amount"])
                total_sent = sum(t["receiver_amount"] for t in transactions_two)
                cash_balance = agent_object.current_balance

        else:
            if teller:
                till_name = teller[0].select_till
                till_object = frappe.get_doc("Till", till_name)
                if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                float_balance = till_object.current_balance
                transactions = frappe.get_all("Transaction",
                                              filters={"owner": user.email,
                                                       "posting_date":frappe.utils.now(),
                                                       "cash_in": 1,
                                                        "docstatus": 1
                                                       }, fields=["amount"])
                total_received = sum(t["amount"] for t in transactions)
                transactions_two = frappe.get_all("Transaction",
                                              filters={"withdrawn_by": user.email,
                                                       "withdrawal_date":frappe.utils.now(),
                                                       "cash_out": 1,
                                                         "docstatus": 1
                                                       }, fields=["receiver_amount"])
                total_sent = sum(t["receiver_amount"] for t in transactions_two)
                cash_balance = till_object.current_balance
            else:
                pass

    if user != "Administrator":
        # total_cash_balance = float_balance + cash_balance
        total_cash_balance = cash_balance
        
        results = {
			"float_balance": f"$ {total_cash_balance}",
			"total_received": f"$ {total_received}",
			"total_sent": f"$ {total_sent}",
			"cash_balance": f"$ {cash_balance}",
		}
        return results


@frappe.whitelist()
def get_user_till():
    user = frappe.session.user
    till = frappe.get_all("Teller", filters={"name": user}, fields=["select_till"], limit=1)
    return till[0] if till else None




@frappe.whitelist()
def create_or_open_reconciliation(till):
    today_date = today()
    # Function to generate a new name with incremented suffix
    till_doc = frappe.get_doc("Till", till)
    print("_______________________till_doc.current_balance______________", till_doc.current_balance)
    def generate_new_name(base_name):
        # Fetch existing documents to find the highest suffix
        existing_docs = frappe.get_all("Till Reconciliation", filters={
            "name": ["like", f"{base_name}%"]
        }, fields=["name"])
        
        # Extract suffixes and find the maximum
        suffixes = []
        for doc in existing_docs:
            if '-' in doc.name:
                suffix = doc.name.rsplit('-', 1)[-1]
                if suffix.isdigit():
                    suffixes.append(int(suffix))
        
        # Determine the next suffix
        next_suffix = max(suffixes, default=0) + 1
        return f"{base_name}-{next_suffix}"
    
    # Function to calculate totals for the day
    def calculate_totals():
        cash_in = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) FROM `tabTransaction`
            WHERE owner=%s AND cash_in=1 AND posting_date = %s
        """, (frappe.session.user, today_date))[0][0]

        cash_out = frappe.db.sql("""
            SELECT COALESCE(SUM(receiver_amount), 0) FROM `tabTransaction`
            WHERE withdrawn_by=%s AND cash_out=1 AND withdrawal_date = %s
        """, (frappe.session.user, today_date))[0][0]

        allocations = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) FROM `tabFloat Allocation`
            WHERE to_till=%s AND posting_date = %s AND docstatus=1 AND destination_type = 'Till'
        """, (till, today_date))[0][0]
        
        from_til_allocations = frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) FROM `tabFloat Allocation`
            WHERE from_till=%s AND posting_date = %s AND docstatus=1 AND source_type = 'Till'
        """, (till, today_date))[0][0]
        
        charges = frappe.db.sql("""
            SELECT COALESCE(SUM(charge), 0) FROM `tabTransaction`
            WHERE owner=%s AND cash_in=1 AND posting_date = %s
        """, (frappe.session.user, today_date))[0][0]

        return cash_in, cash_out, allocations, charges, from_til_allocations

    # Check if a reconciliation exists for today
    recon = frappe.get_all("Till Reconciliation", filters={
        "till": till,
        "posting_date": today_date,
    }, fields=["name", "docstatus"], limit=1)
    print("__________________________reco____________", recon)
    # if recon:
    #     recon_doc = frappe.get_doc("Till Reconciliation", recon[0].name)
    #     if recon_doc.docstatus == 0:
    #         cash_in, cash_out, allocations, charges = calculate_totals()
    #         opening_balance = till_doc.opening_balance #recon_doc.opening_balance
    #         calculated = opening_balance + allocations + cash_in - cash_out
    #         recon_doc.docstatus = 0
    #         recon_doc.total_commission = charges
    #         recon_doc.transaction_status = "Pending"
    #         recon_doc.closing_float = till_doc.current_balance # float balance
    #         recon_doc.total_cash_in = cash_in
    #         recon_doc.total_cash_out = cash_out
    #         recon_doc.allocations_received = allocations
    #         recon_doc.closing_balance = calculated
    #         recon_doc.save(ignore_permissions=True)
    #         return recon_doc
    #     elif recon_doc.docstatus == 2:
    #         # previous = frappe.get_all("Till Reconciliation", filters={
    #         #     "till": till,
    #         #     "docstatus": 1
    #         # }, order_by="posting_date desc", limit=1, fields=["closing_balance"])
    #         # opening_balance = previous[0]["closing_balance"] if previous else 0.0
    #         # Create a new version of the canceled document
    #         cash_in, cash_out, allocations, charges = calculate_totals()
    #         opening_balance = till_doc.opening_balance #recon_doc.opening_balance
    #         calculated = opening_balance + allocations + cash_in - cash_out
    #         new_doc = frappe.copy_doc(recon_doc)
    #         new_doc.workflow_state = "Draft"  # Adjust to your workflow state
    #         new_doc.name = None  # Reset the name to create a new document
    #         # Create a new name based on the existing name
    #         base_name = recon_doc.name
    #         if '-' in base_name:
    #             base_name = base_name.rsplit('-', 1)[0]
    #         new_doc.name = generate_new_name(base_name)  # Generate new name with suffix
            
    #         # Set the "Amended From" field
    #         new_doc.amended_from = recon_doc.name
    #         new_doc.docstatus = 0
    #         new_doc.total_commission = charges
    #         new_doc.transaction_status = "Pending"
    #         new_doc.closing_float = till_doc.current_balance # float balance
    #         new_doc.total_cash_in = cash_in
    #         new_doc.total_cash_out = cash_out
    #         new_doc.allocations_received = allocations
    #         new_doc.closing_balance = calculated
    #         new_doc.insert(ignore_permissions=True)
    #         return new_doc
    #     else:
    #         pass
            
    # else:
    #     previous = frappe.get_all("Till Reconciliation", filters={"till": till}, 
    #                                order_by="posting_date desc", limit=1, fields=["closing_balance"])
    #     # opening_balance = previous[0]["closing_balance"] if previous else 0.0
    #     opening_balance = till_doc.opening_balance

    # Calculate totals for the day
    opening_balance = till_doc.opening_balance
    cash_in, cash_out, allocations, charges, from_til_allocations = calculate_totals()
    calculated = opening_balance + allocations + cash_in - cash_out - from_til_allocations # TO DO -subtract remittance amount # Done Deal
    
    # Create new Till Reconciliation doc
    doc = frappe.get_doc({
        "doctype": "Till Reconciliation",
        "till": till,
        "date": today_date,
        "opening_balance": opening_balance,
        "total_cash_in": cash_in,
        "total_cash_out": cash_out,
        "allocations_received": allocations,
        "closing_balance": calculated,
        "remitted_amount": from_til_allocations,
        "till_operator": frappe.session.user,
        "total_commission": charges,
        "closing_float": till_doc.current_balance,
        "posting_date": today_date
    })
    doc.insert(ignore_permissions=True)
    return doc
# @frappe.whitelist()
# def create_or_open_reconciliation(till):
#     # Check if one exists for today
#     recon = frappe.get_all("Till Reconciliation", filters={
#         "till": till,
#         "posting_date": today(),
#     }, fields=["name"], limit=1)

#     if recon:
#         if recon[0].docstatus == 0:
#             return frappe.get_doc("Till Reconciliation", recon[0].name)
#         elif recon[0].docstatus == 2:
#             previous = frappe.get_all("Till Reconciliation", filters={
#                     "till": till,
#                     "docstatus": 1
#                 }, order_by="posting_date desc", limit=1, fields=["closing_balance"])
#             opening_balance = previous[0]["closing_balance"] if previous else 0.0
#                 # Calculate totals for the day (example: adjust to real Doctype)
#             cash_in = frappe.db.sql("""
#                 SELECT COALESCE(SUM(amount), 0) FROM `tabTransaction`
#                 WHERE owner=%s AND cash_in=1 AND posting_date = %s
#             """, (frappe.session.user, today()))[0][0]


#             cash_out = frappe.db.sql("""
#                 SELECT COALESCE(SUM(receiver_amount), 0) FROM `tabTransaction`
#                 WHERE withdrawn_by=%s AND cash_out=1 AND posting_date = %s
#             """, (frappe.session.user, today()))[0][0]

#             allocations = frappe.db.sql("""
#                 SELECT COALESCE(SUM(amount), 0) FROM `tabFloat Allocation`
#                 WHERE to_till=%s AND posting_date = %s AND docstatus=1 AND destination_type = 'Till'
#             """, (till, today()))[0][0]

#             calculated = opening_balance + allocations + cash_in - cash_out

#             # Create new Till Reconciliation doc
#             doc = frappe.get_doc({
#                 "doctype": "Till Reconciliation",
#                 "till": till,
#                 "date": today(),
#                 "opening_balance":  opening_balance,
#                 "total_cash_in": cash_in,
#                 "total_cash_out": cash_out,
#                 "allocations_received": allocations,
#                 "closing_balance": calculated,
#                 "till_operator": frappe.session.user,
#                 "posting_date": today()
#             })
#             doc.insert(ignore_permissions=True)
#             return doc

#     # Fetch opening balance from previous day's reconciliation
#     previous = frappe.get_all("Till Reconciliation", filters={
#         "till": till
#     }, order_by="posting_date desc", limit=1, fields=["closing_balance"])

#     opening_balance = previous[0]["closing_balance"] if previous else 0.0

#     # Calculate totals for the day (example: adjust to real Doctype)
#     cash_in = frappe.db.sql("""
#         SELECT COALESCE(SUM(amount), 0) FROM `tabTransaction`
#         WHERE owner=%s AND cash_in=1 AND posting_date = %s
#     """, (frappe.session.user, today()))[0][0]


#     cash_out = frappe.db.sql("""
#         SELECT COALESCE(SUM(receiver_amount), 0) FROM `tabTransaction`
#         WHERE withdrawn_by=%s AND cash_out=1 AND posting_date = %s
#     """, (frappe.session.user, today()))[0][0]

#     allocations = frappe.db.sql("""
#         SELECT COALESCE(SUM(amount), 0) FROM `tabFloat Allocation`
#         WHERE to_till=%s AND posting_date = %s AND docstatus=1 AND destination_type = 'Till'
#     """, (till, today()))[0][0]

#     calculated = opening_balance + allocations + cash_in - cash_out

#     # Create new Till Reconciliation doc
#     doc = frappe.get_doc({
#         "doctype": "Till Reconciliation",
#         "till": till,
#         "date": today(),
#         "opening_balance":  opening_balance,
#         "total_cash_in": cash_in,
#         "total_cash_out": cash_out,
#         "allocations_received": allocations,
#         "closing_balance": calculated,
#         "till_operator": frappe.session.user,
#         "posting_date": today()
#     })
#     doc.insert(ignore_permissions=True)
#     return doc

@frappe.whitelist()
def get_exchange_rate():
    currencies = frappe.get_all("Currency", filters={
            "enabled": 1,
            "currency_name": ["!=", "USD"] #exclude base currency
        }, fields=["currency_name", "fraction_units", "symbol"])
    return currencies