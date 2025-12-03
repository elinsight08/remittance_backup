// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer", {
	// refresh(frm) {

	// },
    validate: function(frm) {
        if (frm.doc.date_of_birth) {
            const dob = new Date(frm.doc.date_of_birth);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();  // Use 'let' instead of 'const'
            const monthDiff = today.getMonth() - dob.getMonth();

            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                age--;
            }

            if (age < 10) {
                frappe.msgprint(__('Date of Birth must be at least 10 years ago.'));
                frappe.validated = false;
            }
        }
    },

    customer_type: function(frm) {
        if (frm.doc.customer_type === 'Company') {
            frm.set_value('identification_type', 'Company Reg No');
        } else if (frm.doc.customer_type === 'Individual') {
            frm.set_value('identification_type', 'National ID'); // Set to "ID Number" for individuals
        } else {
            frm.set_value('identification_type', ''); // Clear the field for other types
        }
    }
});
