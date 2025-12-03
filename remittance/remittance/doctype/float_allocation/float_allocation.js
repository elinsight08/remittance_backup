// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt


frappe.ui.form.on('Float Allocation', {
	onload(frm) {
		if (frappe.session.user !== "Administrator") {
			if (frappe.user.has_role('Finance Manager')) {
				frm.set_value('source_type', 'Branch');
				frm.set_df_property('source_type', 'read_only', 1);

				frm.set_value('from_branch', 'Crediconnect');
				frm.set_df_property('from_branch', 'read_only', 1);

				frm.set_value('destination_type', 'Branch');
				frm.set_df_property('destination_type', 'read_only', 1);

				frm.set_value('to_branch', 'Tyche HQ');
				frm.set_df_property('to_branch', 'read_only', 1);

				frm.set_value('default_branch', 'Tyche HQ');
			}
		}
        
    },
    refresh: function(frm) { // Triggered when the form is refreshed/loaded
        apply_user_filter(frm); // Call the filtering function
		// let agent =  frappe.session.user;
		frappe.db.get_doc("User", frappe.session.user)
		.then(user => {
			// console.log("user", user);
			if (user.is_agent) {
				frappe.db.get_doc("Agent", user.agent)
				.then(agent => {
					console.log("agent", agent);
					if (agent.agent_type == "Individual") {
						console.log("Individual Agent t");
						frm.set_df_property('company', 'read_only', 1);
						//change lable to "Branch"
						frm.set_df_property('company', 'label', 'Agent');
						frm.set_df_property('default_branch', 'reqd', 0);

					};
					console.log("Individual Agent r");
				});



			}

		});

    },



});

function apply_user_filter(frm) {
	frm.set_query('company', function() {
		return {
		  filters: {
			is_agent: 0
		  }
		};
	  });

	  frm.set_query('default_branch', function() {
		return {
		  filters: {
			"company": '' + frm.doc.company + '',
		  }
		};
	  });



}
