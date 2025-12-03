# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CommissionDisbursement(Document):
	def validate(self):
		"""
		Function to validate the commission disbursement amount against the agent's balance.
		Raises an error if the amount exceeds the agent's available balance.
		"""
		agent_object = frappe.get_doc("Agent", self.agent)
		if self.disbursement_amount > agent_object.balance:
			frappe.throw(f"Insufficient balance for agent {self.agent}. Available balance: {agent_object.balance}")

	def on_submit(self):
		"""
		Function to update the commission disbursement status to 'Paid' when the document is submitted.
		"""
		agent_object = frappe.get_doc("Agent", self.agent)
		agent_object.balance -= self.disbursement_amount
		agent_object.save()
