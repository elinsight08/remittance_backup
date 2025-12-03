// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Branch', {
    refresh: function(frm) { // Triggered when the form is refreshed/loaded
        apply_user_filter(frm); // Call the filtering function
        toggle_add_row_button(frm);

		frappe.db.get_doc("User", frappe.session.user)
            .then(user => {
                if (user.is_agent) {
                    frm.set_df_property('company', 'hidden', 1);
                }
            });
    },
    branch_name: function(frm) { // Triggered when the 'branch_name' field changes
        apply_user_filter(frm); // Call the filtering function
    },
	//if  login user is_agent, hide the branch name field

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




function apply_user_filter(frm) {
	frm.set_query('company', function() {
		return {
		  filters: {
			is_agent: 0
		  }
		};
	  });
    if (frm.doc.branch_name) {
        frm.set_query('user', 'primary_contact_person', function() {
            return {
                filters: {
                    'branch': frm.doc.branch_name
                }
            };
        });
    } else {
        // Optional: Clear the filter if no branch is selected
        frm.set_query('user', 'primary_contact_person', function() {
            return {
                filters: {
                    'name': 'No User Found'
                }
            };
        });
    }
}
