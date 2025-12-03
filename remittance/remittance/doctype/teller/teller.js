// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Teller", {
	refresh(frm) {
		frappe.db.get_doc("User", frappe.session.user)
		.then(user => {
			if (user.is_agent) {
				//set label for agent
				frappe.db.get_doc("Agent", user.agent)
				.then(agent => {
					if (agent.agent_type == "Company") {
						frm.set_df_property('branch', 'reqd', 1);
					}
				}
				);


			}
		});
	},
});
