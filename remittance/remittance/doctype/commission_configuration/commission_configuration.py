# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CommissionConfiguration(Document):

	def before_save(self):
		"""Hook method triggered before saving the document."""
		user = frappe.get_doc("User", frappe.session.user)
		if user:
			self.company = user.company

