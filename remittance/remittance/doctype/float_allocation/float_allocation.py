# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FloatAllocation(Document):
	def validate(self):
		"""Hook method triggered before saving the document."""
		# if self.destination_type == "Agent":
		# 	agent = frappe.get_doc("Agent", self.to_agent)
		# 	if agent.current_balance > agent.threshold_min:
		# 		frappe.throw("Minimum threshold must exceed current balance for float allocation.")
		# elif self.destination_type == "Branch":
		# 	branch = frappe.get_doc("Branch", self.to_branch)
		# 	if branch.current_balance > branch.threshold_min:
		# 		frappe.throw("Minimum threshold must exceed current balance for float allocation.")
		# elif self.destination_type == "Till":
		# 	till = frappe.get_doc("Till", self.to_till)
		# 	if till.current_balance > till.threshold_min:
		# 		frappe.throw("Minimum threshold must exceed current balance for float allocation.")

		if self.source_type == "Agent":
			self.validate_agent()
		elif self.source_type == "Branch":
			self.validate_branch()
		elif self.source_type == "Till":
			self.validate_till()
		else:
			frappe.throw("Invalid source type. Please select either Agent, Branch, or Till.")


	def validate_agent(self):
		"""Validate the agent's float allocation."""
		if self.from_agent == self.to_agent:
			frappe.throw("Source and destination agents cannot be the same.")
		agent = frappe.get_doc("Agent", self.from_agent)

		if agent.current_balance < self.amount:
			frappe.throw(f"Insufficient balance in agent {self.from_agent}. Current balance: {agent.current_balance}")


	def validate_branch(self):
		"""Validate the branch's float allocation."""
		# if self.from_branch == self.to_branch:
		# 	frappe.throw("Source and destination branches cannot be the same.")
		branch = frappe.get_doc("Branch", self.from_branch)
		if not "Finance Manager" in frappe.get_roles():
			if branch.current_balance < self.amount:
				frappe.throw(f"Insufficient balance in branch {self.from_branch}. Current balance: {branch.current_balance}")


	def validate_till(self):
		"""Validate the till's float allocation."""
		if self.from_till == self.to_till:
			frappe.throw("Source and destination tills cannot be the same.")
		till = frappe.get_doc("Till", self.from_till)
		if till.current_balance < self.amount:
			frappe.throw(f"Insufficient balance in till {self.from_till}. Current balance: {till.current_balance}")


	def on_submit(self):
		"""Hook method triggered after submitting the document."""
		print("Float allocation entry created successfully.")
		if self.destination_type == "Agent":
			self.update_agent_float_allocation()
		elif self.destination_type == "Branch":
			self.update_branch_float_allocation()
		elif self.destination_type == "Till":
			self.update_till_float_allocation()
		else:
			frappe.throw("Invalid source type. Please select either Agent, Branch, or Till.")

	def update_agent_float_allocation(self):
		"""Update the agent's float allocation."""
		print("Updating agent float allocation...")
		agent = frappe.get_doc("Agent", self.to_agent)
		agent.current_balance += self.amount
		agent.save()
		self.update_source_float_allocation()
		frappe.db.commit()

	def update_branch_float_allocation(self):
		"""Update the branch's float allocation."""
		branch = frappe.get_doc("Branch", self.to_branch)
		branch.current_balance += self.amount
		branch.save()
		self.update_source_float_allocation()
		frappe.db.commit()

	def update_till_float_allocation(self):
		"""Update the till's float allocation."""
		till = frappe.get_doc("Till", self.to_till)
		till.current_balance += self.amount
		till.save()
		self.update_source_float_allocation()
		frappe.db.commit()

	#update the source float allocation
	def update_source_float_allocation(self):
		"""Update the source float allocation."""
		if self.source_type == "Agent":
			agent = frappe.get_doc("Agent", self.from_agent)
			agent.current_balance -= self.amount
			agent.save()
			frappe.db.commit()
			send_alert_min_threshold("Agent", agent.name)
		elif self.source_type == "Branch":
			if not "Finance Manager" in frappe.get_roles():
				branch = frappe.get_doc("Branch", self.from_branch)
				branch.current_balance -= self.amount
				branch.save()
				frappe.db.commit()
				send_alert_min_threshold("Branch", branch.name)
		elif self.source_type == "Till":
			till = frappe.get_doc("Till", self.from_till)
			till.current_balance -= self.amount
			till.save()
			frappe.db.commit()
			send_alert_min_threshold("Till", till.name)
		else:
			frappe.throw("Invalid source type. Please select either Agent, Branch, or Till.")


def send_alert_min_threshold(doctype, docname):
	if doctype == "Agent":
		if agent := frappe.get_doc("Agent", docname):
			if agent.current_balance < agent.threshold_min:
				roles = ["Agent Manager", "Agent Supervisor"]
				recipients = get_users_with_roles_company(roles, agent.name)
				if agent.current_balance < agent.threshold_min:
					send_balance_alert(
						recipients=recipients,
						subject="Balance Alert",
						current_balance=agent.current_balance,
						threshold=agent.threshold_min,
						is_till=False
					)
	elif doctype == "Branch":
		if branch := frappe.get_doc("Branch", docname):
			if branch.current_balance < branch.threshold_min:
				roles = ["Branch Manager", "Agent Manager"]
				recipients = get_users_with_roles_branch(roles, branch.name)
				send_balance_alert(
					recipients=recipients,
					subject="Balance Alert",
					current_balance=branch.current_balance,
					threshold=branch.threshold_min,
					is_till=False
				)
	elif doctype == "Till":
		if till := frappe.get_doc("Till", docname):
			if till.current_balance < till.threshold_min:
				roles = ["Branch Manager", "Agent Manager"]
				recipients = get_users_with_roles_branch(roles, till.branch)
				print(f"Recipients: {recipients} banch : {till.branch}")
				send_balance_alert(
					recipients=recipients,
					subject="Balance Alert",
					current_balance=till.current_balance,
					threshold=till.threshold_min,
					is_till=True,
					till_name=till.name
				)
				print("Alert sent for Till")


def get_users_with_roles_branch(roles, branch):
    users = frappe.db.sql("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON u.name = hr.parent
        WHERE hr.role IN %(roles)s
        AND u.branch = %(branch)s
    """, {"roles": roles, "branch": branch})
    return [user[0] for user in users] if users else []

def get_users_with_roles_company(roles, company):
    users = frappe.db.sql("""
        SELECT DISTINCT u.email
        FROM `tabUser` u
        JOIN `tabHas Role` hr ON u.name = hr.parent
        WHERE hr.role IN %(roles)s
        AND u.company = %(company)s
    """, {"roles": roles, "company": company})
    return [user[0] for user in users] if users else []

def send_balance_alert(recipients, subject, current_balance, threshold, is_till, till_name=None):
    message = (
        f"Your till {till_name} has a balance of {current_balance}. "
        f"Please ensure it is above the minimum threshold of {threshold}."
    ) if is_till else (
        f"Your float balance is {current_balance}. "
        f"Please ensure it is above the minimum threshold of {threshold}."
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )

