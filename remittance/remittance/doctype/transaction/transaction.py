# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt
import math
import frappe
from  remittance.utils.mails import custom_send_mail
import string
import random
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import frappe.realtime
from frappe.utils import now

class Transaction(Document):
    def before_rename(self, current_name, updated_name, merge):
        frappe.throw("Renaming this DocType is not allowed.")
    def autoname(self):
        # Generate a unique random string of length 6
        self.name = self.generate_unique_name()

    def _send_sms(self):
        formatted_amount = frappe.format(self.receiver_amount, {"fieldtype": "Currency", "options": self.currency})
        msg = f"{self.sender_name} sent you {self.currency}{formatted_amount}. Trans Ref {self.name}. Collect at any Tyche Connect outlet listed on www.tycheconnect.co.zw"

        receiver_list = [self.mobile_no]
        if self.mobile_no:
            send_sms(receiver_list, msg)
    
    def validate_id(self,data):
        import re
        pattern = r'^\d{2}\d{5,10}[a-zA-Z]\d{2}$'
        
        if re.match(pattern, data):
            return True

    def validate(self):
        if self.amount <= 0:
            frappe.throw("Transaction amount must be greater than zero.")

        
        if frappe.session.user != "Administrator":
            user = frappe.get_doc("User", frappe.session.user)
            teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])

            if user.is_agent:
                if teller:
                    till_name = teller[0].select_till
                    till_object = frappe.get_doc("Till", till_name)
                    self.created_till= till_name
                    if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")
                    if self.cash_out ==1:
                        if till_object.current_balance < self.amount:
                            frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    agent_object = frappe.get_doc("Agent", user.agent)
                    if self.cash_out ==1:
                        if agent_object.current_balance < self.amount:
                            frappe.throw(f"Insufficient balance in agent {user.agent}. Current balance is {agent_object.current_balance}.")
            else:
                if teller:
                    till_name = teller[0].select_till
                    till_object = frappe.get_doc("Till", till_name)
                    self.created_till= till_name
                    if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")
                    if self.cash_out ==1:
                        if till_object.current_balance < self.amount:
                            frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    frappe.throw("User does not have a till assigned.")

    def on_submit(self):
        """Hook method triggered after submitting the document."""
       

        #send sms
        self._send_sms()
        data = {
			"transaction_type":"Cash-In",
			"ref_doc": self.name,
			"trans_amount": self.amount,
			"branch": self.created_branch
		}
        create_agent_commission(data)
        self.update_cash_hand_balance()
        send_alert_max_threshold()


    def update_cash_hand_balance(self):
        """Update the cash hand balance for the teller or agent."""
        if frappe.session.user != "Administrator":
            user = frappe.get_doc("User", frappe.session.user)
            teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])
            
            if user.is_agent:
                if teller:
                    till_name = teller[0].select_till
                    # self.update_sender_till(till_name)
                    till_object = frappe.get_doc("Till", till_name)
                    till_object.cash_in_hand += self.amount
                    till_object.current_balance += self.amount
                    till_object.save()
                else:
                    agent_object = frappe.get_doc("Agent", user.agent)
                    agent_object.cash_in_hand += self.amount
                    agent_object.current_balance += self.amount
                    agent_object.save()
            else:
                if teller:
                    till_name = teller[0].select_till
                    till_object = frappe.get_doc("Till", till_name)
                    till_object.cash_in_hand += self.amount
                    till_object.current_balance += self.amount
                    till_object.save()
            frappe.db.commit()

    def deduct_float(self):
        """Deduct the float from the teller or agent."""
        if frappe.session.user != "Administrator":
            user = frappe.get_doc("User", frappe.session.user)
            teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])
            if user.is_agent:
                if teller:
                    till_name = teller[0].select_till
                   
                    till_object = frappe.get_doc("Till", till_name)
                    till_object.current_balance -= self.receiver_amount
                    till_object.save()
                else:
                    agent_object = frappe.get_doc("Agent", user.agent)
                    agent_object.current_balance -= self.receiver_amount
                    agent_object.save()
            else:
                if teller:
                    till_name = teller[0].select_till
                
                    till_object = frappe.get_doc("Till", till_name)
                    till_object.current_balance -= self.receiver_amount
                    till_object.save()

            frappe.db.commit()
            send_alert_min_threshold()

    def before_insert(self):
        """Hook method triggered before saving the document."""
        #assign user branch from session
        self.posting_date = frappe.utils.now()
        self.cash_in = 1
        
        if frappe.session.user != "Administrator":
            user = frappe.get_doc("User", frappe.session.user)
            
            if user.branch:
                self.created_branch = user.branch
            else:
                self.created_branch = ''

    def generate_unique_name(self):
        while True:
            # Generate a random string of 5 digits
            random_digits = ''.join(random.choices('0123456789', k=6))
            unique_name = f"TC{random_digits}"

            # Check if the name already exists
            if not frappe.db.exists("Transaction", unique_name):
                return unique_name
                

    def _set_receiver_name(self):
        if self.recipient_type == 'Recipients':
            self.receiver_name = f'{self.first_name} {self.last_name or ""}'.strip()
            self.receiver_id = self.national_id
        elif self.recipient_type == 'Unregistered Customer':
            if not self.validate_id(self.un_national_id):
                frappe.throw("Invalid recipient National ID format for. It should be in the format 1234567890X00")
            self.receiver_name = f'{self.un_first_name} {self.un_last_name or ""}'.strip()
            self.receiver_id = self.un_national_id
        else:
            raise ValueError(f"Invalid customer type: {self.customer_type}")

    def before_save(self):
        """Hook method triggered before saving the document."""
        self._set_receiver_name()

    def after_insert(self):
        if self.recipient_type == 'Unregistered Customer':
            self.create_recipient(self.customer,self.un_first_name, self.un_last_name, self.mobile_no, self.un_national_id)

    def create_recipient(self, customer, first_name, last_name, phone_number, national_id):
        """Create a new recipient."""
        print("creating recipient")
        recipient = frappe.get_doc({
			'doctype': 'Recipient',
			'sender_id': customer,
			'first_name': first_name,
			'last_name': last_name,
			'mobile_no': phone_number,
            'national_id': national_id
		})
        print("saved", recipient)
        recipient.insert(
            ignore_permissions=True,
			# ignore_validate=True,
		)

def send_collected_money_sms(receiver_name, receiver_amount, doc_name, sender_id):
        # formatted_amount = frappe.format(self.receiver_amount, {"fieldtype": "Currency", "options": self.currency})
        msg = f"{receiver_name}, has collected USD {receiver_amount} for Trans Ref {doc_name}."
        sender_doc = frappe.get_doc('Customer', sender_id)
        phone_number = sender_doc.mobile_no
        receiver_list = [phone_number]
        if phone_number:
            send_sms(receiver_list, msg)

@frappe.whitelist()
def withdraw(docname): 
    withdrawn_branch = ""
    withdrawn_by = ""
    withdrawn_till = ""
    transaction_object = frappe.get_doc("Transaction", docname)
    user = frappe.get_doc("User", frappe.session.user)
    teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])
    if frappe.session.user != "Administrator":
        withdrawn_by = user.email
        if user.branch:
            withdrawn_branch = user.branch
        if user.is_agent:
            if teller:
                till_name = teller[0].select_till
                withdrawn_till= till_name
                till_object = frappe.get_doc("Till", till_name)
                withdrawn_branch = till_object.branch
                if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                if till_object.current_balance < transaction_object.receiver_amount:
                    frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    till_object.current_balance -= transaction_object.receiver_amount
                    till_object.save()
            else:
                agent_object = frappe.get_doc("Agent", user.agent)
                if agent_object.current_balance < transaction_object.receiver_amount:
                    frappe.throw(f"Insufficient balance in agent {user.agent}. Current balance is {agent_object.current_balance}.")
                else:
                    agent_object.current_balance -= transaction_object.receiver_amount
                    agent_object.save()
        else:
            if teller:
                till_name = teller[0].select_till
                withdrawn_till = till_name
                till_object = frappe.get_doc("Till", till_name)
                withdrawn_branch = till_object.branch
                if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                if till_object.current_balance < transaction_object.receiver_amount:
                     frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    print("about to update..")
                    till_object.current_balance -= transaction_object.receiver_amount
                    till_object.save()
                    print("updated")
            else:
                frappe.throw("User does not have a till assigned.")


    data = {
		"transaction_type":"Cash-Out",
		"ref_doc": docname,
		"trans_amount": transaction_object.amount,
		"branch": withdrawn_branch
	}
    try:
        create_agent_commission(data)
    except Exception as e:
        pass


	# Update the transaction status to "Completed Or Reversed"
    transaction_status= 'Completed' if transaction_object.transaction_status == 'Pending' else 'Reversed'
    frappe.db.sql("""
        UPDATE `tabTransaction`
        SET transaction_status = %s,
            withdrawal_date = %s,
            withdrawn_till = %s,
            withdrawn_branch = %s,
			withdrawn_by = %s,
            cash_out = 1
        WHERE name = %s AND docstatus = 1
    """, (transaction_status, frappe.utils.now(),withdrawn_till, withdrawn_branch, withdrawn_by, docname))
    # Send SMS to the receiver
    send_collected_money_sms(transaction_object.receiver_name, transaction_object.receiver_amount, docname, transaction_object.customer)
    # Notify about minimum threshold
    send_alert_min_threshold()
    frappe.clear_document_cache("Transaction", docname)

@frappe.whitelist()
def calculate_fee(receiver_amount):
    try:
        fee = frappe.get_doc("Transfer Fee")
        print("fee", fee.charge_type)
        if fee.charge_type == "Percentage":
            charge = (fee.percentage / 100) * float(receiver_amount)
        elif fee.charge_type == "Flat Fee":
            charge = fee.flat_fee
        elif fee.charge_type == "Bands":
            charge = calculate_band_charge(fee, receiver_amount) # Call helper function
        else:
            charge = 0.0
        return charge
    except:
        charge = 0.0
@frappe.whitelist()
def calculate_receiver_fee(amount):
    try:
        fee = frappe.get_doc("Transfer Fee")
        print("fee", fee.charge_type)
        if fee.charge_type == "Percentage":
            charge = (fee.percentage / 100) * float(amount)
        elif fee.charge_type == "Flat Fee":
            charge = fee.flat_fee
        elif fee.charge_type == "Bands":
            charge = calculate_band_charge(fee, amount) # Call helper function
        else:
            charge = 0.0
        return charge
    except:
        charge = 0.0

def calculate_band_charge(fee, amount):
    """Calculates the charge based on the defined bands."""
    bands = fee.get("bands")  # Assuming your child table is named "bands"
    if not bands:
        print("No bands defined for Transfer Fee")
        return frappe.throw(
			"No bands defined for Transfer Fee"
		)

    is_amount_valid_for_bands = lambda fee, amount: any(
		(band.lower_limit <= float(amount)) and
		(band.upper_limit in (None, 0) or  # Check for open upper limit
		(band.upper_limit and float(amount) <= band.upper_limit))
		for band in fee.get("bands", [])
	)
    if not is_amount_valid_for_bands(fee, amount):
        return frappe.throw(
			f"Amount {amount} does not fall within any defined band for {fee.name}"
		)

    for band in bands:
        lower_limit = band.lower_limit
        upper_limit = band.upper_limit

        # fixed_amount = band.fixed_amount  # Assuming the fee amount field is named "fixed_amount"

        if lower_limit is not None and upper_limit is not None:
            if lower_limit <= float(amount) <= upper_limit:
                print(f"Amount {amount} falls within band: {lower_limit} - {upper_limit}")
                if band.charge_type == "Percentage":
                    charge = (band.percentage / 100) * float(amount)
                elif band.charge_type == "Fixed Amount":
                    charge = band.fixed_amount
                elif band.charge_type == "Free":
                    charge = 0.0
                else:
                    charge = 0.0
                return charge

    print(f"Amount {amount} does not fall within any defined band.")
    return 0.0  # Or raise an exception, depending on your requirements


def create_agent_commission(data):
    user = frappe.get_doc("User", frappe.session.user)
    if user.is_agent:
        commission_configs = frappe.get_all(
			"Agent",
			filters={"name": user.agent},  # Adjust the filter key based on your DocType's structure
			fields=["withdrawal_commission", "cash_in_commission", "balance"],
			limit=1
		)
        if commission_configs:
            agent_comm = commission_configs[0]
            if  agent_comm:
                comm_percent = 0
                if data["transaction_type"] == 'Cash-Out':
                    comm_percent = agent_comm.withdrawal_commission
                elif data["transaction_type"] == 'Cash-In':
                    comm_percent = agent_comm.cash_in_commission
                if comm_percent != 0:
                    amount = (comm_percent/100) * data["trans_amount"]
                    new_doc = frappe.get_doc({
						'doctype': 'Commission Transaction',
						"transaction_type": data["transaction_type"],
						"ref_doc":data["ref_doc"],
						"comm_percent": comm_percent,
						"amount": amount,
						"posting_date": now(),
						"user": user.email,
						"agent": user.agent,
						"branch":data["branch"]
					})
                    update_agent_commission_balance(user.agent, amount)
                    new_doc.insert(
						ignore_permissions=True
					)

def update_agent_commission_balance(agent, amount):
	"""Update the agent's commission balance."""
	agent_doc = frappe.get_doc("Agent", agent)
	if agent_doc:
		agent_doc.balance += amount
		agent_doc.save()
	else:
		frappe.throw(f"Agent {agent} not found.")

@frappe.whitelist()
def reverse_transaction(docname,reason, apply_fee):

    transaction_object = frappe.get_doc("Transaction", docname)


    reversed_with_charge = 0
    reversal_charge = 0.00
    reversal_amount = transaction_object.receiver_amount
    if apply_fee == "1":
        # reversal_charge = math.ceil(calculate_fee(transaction_object.receiver_amount))
        # reversal_amount = math.floor(transaction_object.receiver_amount - reversal_charge)
        reversal_charge=transaction_object.charge
        reversal_amount = transaction_object.amount
        reversed_with_charge = 1
    user = frappe.get_doc("User", frappe.session.user)
    branch = ""
    company = ""
    if frappe.session.user != "Administrator":
        user = frappe.get_doc("User", frappe.session.user)
        if user and user.branch:
            branch = user.branch
            company = user.company

    frappe.db.sql("""
        UPDATE `tabTransaction`
        SET transaction_status = %s,
            withdrawal_date = %s,
            reversed_with_charge = %s
        WHERE name = %s AND docstatus = 1
    """, ('Pending Reversal', frappe.utils.now(), reversed_with_charge, docname))
    new_doc = frappe.get_doc({
		'doctype': 'Reversal',
		"transaction_id": transaction_object.name,
		"reason": reason,
		"posting_date": frappe.utils.now(),
		"reversal_charge": reversal_charge,
        "reversal_status": "Pending Reversal",
		"amount_inc_charge": transaction_object.amount,
		"receiver_amount": transaction_object.receiver_amount,
		"charge": transaction_object.charge,
		"reversal_amount": reversal_amount,
		"currency": transaction_object.currency,
		"sender_name": transaction_object.sender_name,
        "sender_mobile_no": transaction_object.sender_mobile_no,
		"receiver": transaction_object.receiver_name,
		"receiver_mobile_no": transaction_object.mobile_no,
		"branch": branch,
        "company": company
	})
    new_doc.insert(
		ignore_permissions=True
	)
    new_doc.save()
    return True

# @frappe.whitelist()
# def withdraw_reversal(docname):
    
#     print("_____________revesal____________")
#     reversal_objects = frappe.get_all(
# 		"Reversal",
# 		filters={"transaction_id": docname},  # Adjust the filter key based on your DocType's structure
# 		fields=["reversal_status", "branch", "reversal_amount"],
# 		limit=1
# 	)
#     if reversal_objects:
#         reversal_object = reversal_objects[0]
#         if reversal_object.reversal_status == "Pending Reversal":
#             frappe.throw("Reversal is still pending. Please wait for the reversal to be processed before withdrawing.")
#         else:
#             print("_____________frappe.session.user", frappe.session.user)
#             print("______________reversal_object.branch", reversal_object.branch)
#             print("______________reversal_object.reversal_amount", reversal_object.reversal_amount)
            
#             frappe.db.sql("""
#                 UPDATE `tabTransaction`
#                 SET transaction_status = %s,
#                     withdrawn_by = %s,
#                     withdrawn_branch = %s
#                 WHERE name = %s AND docstatus = 1
#             """, ('Reversed', frappe.session.user, reversal_object.branch, docname))
            
@frappe.whitelist()
def withdraw_reversal(docname): 
    reversal_objects = frappe.get_all(
		"Reversal",
		filters={"transaction_id": docname},  # Adjust the filter key based on your DocType's structure
		fields=["reversal_status", "branch", "reversal_amount"],
		limit=1
	)
    
    if reversal_objects:
        reversal_object = reversal_objects[0]
        if reversal_object.reversal_status == "Pending Reversal":
            frappe.throw("Reversal is still pending. Please wait for the reversal to be processed before withdrawing.")
    
    withdrawn_branch = ""
    withdrawn_by = ""
    withdrawn_till = ""
    transaction_object = frappe.get_doc("Transaction", docname)
    user = frappe.get_doc("User", frappe.session.user)
    teller = frappe.get_all("Teller", filters={"branch":user.branch, "name":  user.email}, fields=["select_till"])
    if frappe.session.user != "Administrator":
        withdrawn_by = user.email
        if user.branch:
            withdrawn_branch = user.branch
        if user.is_agent:
            if teller:
                till_name = teller[0].select_till
                withdrawn_till= till_name
                till_object = frappe.get_doc("Till", till_name)
                withdrawn_branch = till_object.branch
                if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                if till_object.current_balance < transaction_object.receiver_amount:
                    frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    till_object.current_balance -= transaction_object.receiver_amount
                    till_object.save()
            else:
                agent_object = frappe.get_doc("Agent", user.agent)
                if agent_object.current_balance < transaction_object.receiver_amount:
                    frappe.throw(f"Insufficient balance in agent {user.agent}. Current balance is {agent_object.current_balance}.")
                else:
                    agent_object.current_balance -= transaction_object.receiver_amount
                    agent_object.save()
        else:
            if teller:
                till_name = teller[0].select_till
                withdrawn_till = till_name
                till_object = frappe.get_doc("Till", till_name)
                withdrawn_branch = till_object.branch
                if till_object.enabled == 0:
                        frappe.throw(f"The till '{till_name}' is currently closed. Please contact your administrator for assistance.")

                if till_object.current_balance < transaction_object.receiver_amount:
                     frappe.throw(f"Insufficient balance in till {till_name}. Current balance is {till_object.current_balance}.")
                else:
                    print("about to update..")
                    till_object.current_balance -= transaction_object.receiver_amount
                    till_object.save()
                    print("updated")
            else:
                frappe.throw("User does not have a till assigned.")


    data = {
		"transaction_type":"Cash-Out",
		"ref_doc": docname,
		"trans_amount": transaction_object.amount,
		"branch": withdrawn_branch
	}
    try:
        create_agent_commission(data)
    except Exception as e:
        pass


	# Update the transaction status to "Completed Or Reversed"
    transaction_status= 'Reversed'
    frappe.db.sql("""
        UPDATE `tabTransaction`
        SET transaction_status = %s,
            withdrawal_date = %s,
            withdrawn_till = %s,
            withdrawn_branch = %s,
			withdrawn_by = %s,
            cash_out = 1
        WHERE name = %s AND docstatus = 1
    """, (transaction_status, frappe.utils.now(),withdrawn_till, withdrawn_branch, withdrawn_by, docname))
    # Send SMS to the receiver
    # send_collected_money_sms(transaction_object.receiver_name, transaction_object.receiver_amount, docname, transaction_object.customer)
    # Notify about minimum threshold
    send_alert_min_threshold()
    frappe.clear_document_cache("Transaction", docname)

# For sending alerts when the balance goes above the maximum threshold - tills or individual agents
def send_alert_max_threshold():
    user = frappe.get_doc("User", frappe.session.user)

    if user.is_agent:
        handle_agent_case_max(user)
    else:
        handle_non_agent_case_max(user)

def handle_agent_case_max(user):
    if not user.agent:
        return

    agent = frappe.get_doc("Agent", user.agent)
    if not agent:
        return

    if agent.agent_type == "Individual":
        handle_individual_agent_max(agent, user)
    else:
        handle_organizational_agent_max(user)

def handle_non_agent_case_max(user):
    till = get_user_till(user)
    if till and till.cash_in_hand > till.threshold_max:
        send_manager_alert_max(
            till=till,
            allowed_roles=["Branch Manager"],
            branch=user.branch,
            subject="Till Balance Alert"
        )


def handle_individual_agent_max(agent, user):
    if agent.cash_in_hand > agent.threshold_max:
        send_balance_alert_max(
            recipients=user.email,
            subject="Balance Alert",
            cash_in_hand=agent.cash_in_hand,
            threshold=agent.threshold_max,
            is_till=False
        )

def handle_organizational_agent_max(user):
    till = get_user_till(user)
    if till and till.cash_in_hand > till.threshold_max:
        send_manager_alert_max(
            till=till,
            allowed_roles=["Agent Manager"],
            branch=user.branch,
            subject="Till Balance Alert"
        )

def send_manager_alert_max(till, allowed_roles, branch, subject):
    emails = get_users_with_roles(allowed_roles, branch)
    if emails:
        send_balance_alert_max(
            recipients=emails,
            subject=subject,
            cash_in_hand=till.cash_in_hand,
            threshold=till.threshold_max,
            is_till=True,
            till_name=till.name
        )

def send_balance_alert_max(recipients, subject, cash_in_hand, threshold, is_till, till_name=None):
    message = (
        f"Your till {till_name} has cash balance of {cash_in_hand}. "
        f"Please ensure it is below the maximum threshold of {threshold}."
    ) if is_till else (
        f"Your cash balance is {cash_in_hand}. "
        f"Please ensure it is below the maximum threshold of {threshold}."
    )
    frappe.enqueue(
        custom_send_mail,
        recipient=recipients,
        subject=subject,
        content=message
    )

    # frappe.sendmail(
    #     recipients=recipients,
    #     subject=subject,
    #     message=message
    # )


#For sending alerts when the balance goes below the minimum threshold - tills or individual agents
@frappe.whitelist()
def send_alert_min_threshold():
    user = frappe.get_doc("User", frappe.session.user)

    if user.is_agent:
        handle_agent_case(user)
    else:
        handle_non_agent_case(user)

def handle_agent_case(user):
    if not user.agent:
        return

    agent = frappe.get_doc("Agent", user.agent)
    if not agent:
        return

    if agent.agent_type == "Individual":
        handle_individual_agent(agent, user)
    else:
        handle_organizational_agent(user)

def handle_individual_agent(agent, user):
    if agent.current_balance < agent.threshold_min:
        send_balance_alert(
            recipients=[user.email],
            subject="Balance Alert",
            current_balance=agent.current_balance,
            threshold=agent.threshold_min,
            is_till=False
        )

def handle_organizational_agent(user):
    till = get_user_till(user)
    if till and till.threshold_min > till.current_balance:
        send_manager_alert(
            till=till,
            allowed_roles=["Agent Manager"],
            branch=user.branch,
            subject="Till Balance Alert"
        )

def handle_non_agent_case(user):
    till = get_user_till(user)
    if till and till.threshold_min > till.current_balance:
        send_manager_alert(
            till=till,
            allowed_roles=["Branch Manager"],
            branch=user.branch,
            subject="Till Balance Alert"
        )

def get_user_till(user):
    till_name = frappe.get_value(
        "Teller",
        filters={"branch": user.branch, "name": user.name},
        fieldname="select_till"
    )
    return frappe.get_doc("Till", till_name) if till_name else None

def send_manager_alert(till, allowed_roles, branch, subject):
    emails = get_users_with_roles(allowed_roles, branch)
    if emails:
        send_balance_alert(
            recipients=emails,
            subject=subject,
            current_balance=till.current_balance,
            threshold=till.threshold_min,
            is_till=True,
            till_name=till.name
        )

def get_users_with_roles(roles, branch):
    users = frappe.db.sql("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON u.name = hr.parent
        WHERE hr.role IN %(roles)s
        AND u.branch = %(branch)s
    """, {"roles": roles, "branch": branch})
    return [user[0] for user in users] if users else []

def send_balance_alert(recipients, subject, current_balance, threshold, is_till, till_name=None):
    message = (
        f"Your till {till_name} has a balance of {current_balance}. "
        f"Please ensure it is above the minimum threshold of {threshold}."
    ) if is_till else (
        f"Your float balance is {current_balance}. "
        f"Please ensure it is above the minimum threshold of {threshold}."
    )
    frappe.enqueue(
        custom_send_mail,
        recipient=recipients,
        subject=subject,
        content=message
    )

    # frappe.sendmail(
    #     recipients=recipients,
    #     subject=subject,
    #     message=message
    # )

@frappe.whitelist()
def update_recipient_national_id(transaction_name = None, national_id = None,recipient_id = None,mobile_no = None): 
    print("updating recipient national id========================", transaction_name, national_id, recipient_id, mobile_no)
    from frappe import _
    if not transaction_name or not national_id:
        frappe.throw(frappe._("Transaction name and national ID are required"))

    
    if not frappe.db.exists("Transaction", transaction_name):
        frappe.throw(frappe._("Transaction not found"))
    
    try:
        # Use SQL query to update
        if recipient_id:
            frappe.db.sql("""
                UPDATE `tabTransaction`
                SET receiver_id = %s
                WHERE name = %s
            """, (national_id, transaction_name))
        
        
            frappe.db.sql("""
                UPDATE `tabRecipient`
                SET national_id = %s
                WHERE name = %s  
            """, (national_id, recipient_id))
            frappe.db.commit()
        elif mobile_no:
            print("updating recipient national id by mobile no")
            frappe.db.sql("""
                UPDATE `tabTransaction`
                SET un_national_id = %s
                WHERE name = %s
            """, (national_id, transaction_name))
            frappe.db.sql("""
                UPDATE `tabRecipient`
                SET national_id = %s
                WHERE mobile_no = %s
            """, (national_id, mobile_no))
            # Commit the transaction Recipient
            frappe.db.commit()
            
        # Add a comment to track the change
        transaction = frappe.get_doc("Transaction", transaction_name)
        transaction.add_comment("Edit", f"Updated recipient national ID to {national_id}")
        
        return {
            "status": "success"
            # "message": _("Recipient national ID updated successfully")
        }
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Failed to update national ID: {str(e)}", "Transaction Update Error")
        return {
            "status": "error",
            "message": _("Failed to update national ID: {0}").format(str(e))
        }