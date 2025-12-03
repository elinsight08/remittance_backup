# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import  _

class Teller(Document):
    
	def validate(self):
		# check if self.select_till has been assigned to another Teller
		user_doc = frappe.get_doc("User", frappe.session.user)
		if user_doc.is_agent:
			agent = frappe.get_doc("Agent", user_doc.agent)
			if agent.agent_type != "Individual" and not self.branch:
				frappe.throw(_("Branch is required for this agent."))

		# if not self.validate_id(self.national_id):
		# 	frappe.throw(_("Invalid National ID format. It should be in the format 1234567890X09"))
		if not self.validate_email(self.email):
			frappe.throw(_("Invalid email format. Please enter a valid email address."))
      
      

		if self.select_till:
			teller = frappe.get_all("Teller", filters={"branch":self.branch, "select_till": self.select_till, "name": ["!=", self.name]})
			if teller:
				teller_name = teller[0].name
				frappe.throw(_(f"This till has already been assigned to {teller_name}"))
    

	def set_company(self):
		"""Set the company field based on the branch."""
		if self.branch:
			try:
				branch_doc = frappe.get_doc("Branch", self.branch)
				self.company = branch_doc.company
			except:
				frappe.throw(_("Branch {0} does not exist").format(self.branch))
		else:
			frappe.throw(_("Branch is required to set the company."))

	def after_insert(self):
		"""Hook method triggered after inserting the document."""
		self.set_company()
		self.create_user()

	def create_user(self):
		"""Create a user for the agent."""
		if not frappe.db.exists("User", self.email):
			user_doc = frappe.get_doc("User", frappe.session.user)
			if self.user_type == "Branch Manager":
				if user_doc.is_agent:
					# Create a new user
					user = frappe.get_doc({
						"doctype": "User",
						"email": self.email,
						"first_name": self.first_name,
						"last_name": self.last_name,
						"branch": self.branch,
						"enabled": 1,
						"user_type": "Website User",
						"send_welcome_email": 1,
						"company": user_doc.agent,
						"is_agent": 1,
						"agent": user_doc.agent,
					})
					user.insert(ignore_permissions=True)
					assign_user_role(self.email, "Agent User")
					assign_user_role(self.email, "Agent Manager")
				else:
					user = frappe.get_doc({
						"doctype": "User",
						"email": self.email,
						"first_name": self.first_name,
						"last_name": self.last_name,
						"branch": self.branch,
						"enabled": 1,
						"user_type": "Website User",
						"send_welcome_email": 1,
						"company": user_doc.company,
						"is_agent": 0,
					})
					user.insert(ignore_permissions=True)
					assign_user_role(self.email, "Branch Manager")
			elif self.user_type == "Till Operator":
				if user_doc.is_agent:
					# Create a new user
					user = frappe.get_doc({
						"doctype": "User",
						"email": self.email,
						"first_name": self.first_name,
						"last_name": self.last_name,
						"branch": self.branch if self.branch else '',
						"enabled": 1,
						"user_type": "Website User",
						"send_welcome_email": 1,
						"company": user_doc.agent,
						"is_agent": 1,
						"agent": user_doc.agent,
					})
					user.insert(ignore_permissions=True)
					assign_user_role(self.email, "Till Operator")
				else:
					user = frappe.get_doc({
						"doctype": "User",
						"email": self.email,
						"first_name": self.first_name,
						"last_name": self.last_name,
						"branch": self.branch,
						"enabled": 1,
						"user_type": "Website User",
						"send_welcome_email": 1,
						"company": user_doc.company,
						"is_agent": 0,
					})
					user.insert(ignore_permissions=True)
					assign_user_role(self.email, "Till Operator")
	# def validate_id(self,data):
	# 	import re
	# 	pattern = r'^\d{2}\d{5,10}[a-zA-Z]\d{2}$'
        
	# 	if re.match(pattern, data):
	# 		return True

	def  validate_email(self,email):
		import re
		pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		
		if re.match(pattern, email):
			return True

def assign_user_role(user, role):
	"""Assign a role to a user"""
	if not frappe.db.exists("User", user):
		frappe.throw(_("User {0} does not exist").format(user))

	if not frappe.db.exists("Role", role):
		frappe.throw(_("Role {0} does not exist").format(role))
	user_doc = frappe.get_doc("User", user)
	user_doc.append_roles(role)
	user_doc.save(
		ignore_permissions=True
	)
	frappe.clear_cache(user=user)


