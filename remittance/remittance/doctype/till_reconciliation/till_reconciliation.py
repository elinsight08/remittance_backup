# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document



class TillReconciliation(Document):
	def on_submit(self):
		"""
		Custom logic to execute when the document is submitted.
		This can include validation, notifications, or other business logic.
		"""
		self.processed_by = frappe.session.user
		till = frappe.get_doc("Till", self.till)
		if not till:
			frappe.thro("Till {0} does not exist.").format(self.till)
		# till.opening_balance = 0
		# till.current_balance = 0
		# till.closing_balance = 0
		# till.cash_in_hand = 0
		till.enabled = 0
		# till.closing_balance = self.closing_balance
		till.save()
