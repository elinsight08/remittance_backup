// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Company", {
	refresh(frm) {
       toggle_add_row_button(frm);
	},

     banks_add: function(frm) {
        toggle_add_row_button(frm);
    },
    
    banks_remove: function(frm) {
        toggle_add_row_button(frm);
    }
});
function toggle_add_row_button(frm) {
    if (frm.doc.banks && frm.doc.banks.length >= 1) {
        frm.fields_dict['banks'].grid.wrapper.find('.grid-add-row').hide();
    } else {
        frm.fields_dict['banks'].grid.wrapper.find('.grid-add-row').show();
    }
}

