# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Agent(Document):
    def _set_agent_name(self):
        new_agent = f'{self.name}'
        if not frappe.db.exists("Company", new_agent):
            new_company = frappe.new_doc("Company")
            new_company.company_name = new_agent
            new_company.is_agent = 1
            new_company.insert(ignore_permissions=True)

    def before_save(self):
        """Hook method triggered before saving the document."""
        self.company = self.name

    def after_insert(self):
        """Hook method triggered after inserting the document."""
        self._set_agent_name()
        self.save()
        frappe.db.commit()
