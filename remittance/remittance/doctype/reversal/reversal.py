# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import send_sms

class Reversal(Document):
	def _send_sms(self):
		formatted_amount = frappe.format(self.reversal_amount, {"fieldtype": "Currency", "options": self.currency})
		msg = f"Trans Ref {self.transaction_id} for {self.currency}{formatted_amount} to {self.receiver} has successfully been reversed."
		receiver_list = [self.sender_mobile_no]

		if self.sender_mobile_no:
			send_sms(receiver_list, msg)

	def on_submit(self):
		"""
		When the reversal is submitted, send an SMS to the sender.
		"""
		self._send_sms()
