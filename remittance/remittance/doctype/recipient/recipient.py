# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt
# import frappe

from frappe.model.document import Document

class Recipient(Document):
    def _set_customer_name(self):
        """Set the client name based on client type."""
        self.full_name = f'{self.first_name} {self.last_name or ""}'.strip()

    def before_save(self):
        """Hook method triggered before saving the document."""
        self._set_customer_name()

