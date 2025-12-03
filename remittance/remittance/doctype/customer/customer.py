# Copyright (c) 2025, Tafadzwa Barwa and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document


class Customer(Document):
    def before_naming(self):
        self._set_customer_name()

    def _set_customer_name(self):
        """Set the client name based on client type."""
        self.customer_name = f'{self.first_name} {self.last_name or ""}'.strip()
        if self.customer_type == 'Individual':
            self.customer_name = f'{self.first_name} {self.last_name or ""}'.strip()
        elif self.customer_type == 'Company':
            self.customer_name = self.company_name or "Unnamed Company"

        else:
            raise ValueError(f"Invalid customer type: {self.customer_type}")

    def before_save(self):
        """Hook method triggered before saving the document."""
        self._set_customer_name()

    def validate(self):
        """
        Custom validation logic for Customer.
        """
        if self.customer_type == 'Company':
            self.gender = 'Other'
        if self.identification_type == "National ID":
            if not self.validate_id(self.identification_number):
                frappe.throw("Invalid National ID format. It should be in the format 1234567890X09")
            
         
            



    
    def validate_id(self,data):
        import re
        pattern = r'^\d{2}\d{5,10}[a-zA-Z]\d{2}$'
        
        if re.match(pattern, data):
            return True