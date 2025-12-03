// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Till", {
	refresh(frm) {
		frappe.db.get_doc("User", frappe.session.user)
		.then(user => {
			if (user.is_agent) {
				//set label for agent
				frm.set_df_property('company', 'label', __('Agent'));
				frappe.db.get_doc("Agent", user.agent)
				.then(agent => {
					if (agent.agent_type == "Company") {
						frm.set_df_property('branch', 'reqd', 1);
					}
				}
				);


			}
		});
		if (frm.doc.enabled === 1) {
			frm.add_custom_button(__('Close Till'), function() {
			// Show confirmation dialog first
				frappe.confirm(
					__('Are you sure you want to close this Till?'),
					function() {  // Yes
						// Proceed with withdrawal after confirmation
						frappe.call({
							method: 'remittance.remittance.doctype.till.till.close_till',
							args: { docname: frm.doc.name },
							freeze: true,
							freeze_message: __('Closing...'),
							callback: function(r) {
								if (r.exc) {
									frappe.msgprint({
										title: __('Error'),
										indicator: 'red',
										message: r.exc
									});
									return;
								}

								// Force refresh from server
								frm.reload_doc(true, () => {
									frappe.show_alert({
										message: __('Closed Successful'),
										indicator: 'green'
									}, 5);
								});
							}
						});
					},
					function() {  // No
						// Cancel action
						frappe.show_alert(__('Cancelled'), 3);
					}
				);
			}).addClass('btn-custom-reversal-btn');
		}else{
			frm.add_custom_button(__('Re-Open Till'), function() {
				// Show confirmation dialog first
				frappe.confirm(
					__('Are you sure you want to re-open this Till?'),
					function() {  // Yes
						// Proceed with withdrawal after confirmation
						frappe.call({
							method: 'remittance.remittance.doctype.till.till.open_till',
							args: { docname: frm.doc.name },
							freeze: true,
							freeze_message: __('Closing...'),
							callback: function(r) {
								if (r.exc) {
									frappe.msgprint({
										title: __('Error'),
										indicator: 'red',
										message: r.exc
									});
									return;
								}

								// Force refresh from server
								frm.reload_doc(true, () => {
									frappe.show_alert({
										message: __('Open Successful'),
										indicator: 'green'
									}, 5);
								});
							}
						});
					},
					function() {  // No
						// Cancel action
						frappe.show_alert(__('Cancelled'), 3);
					}
				);
			}).addClass('btn tf-cash-out-btn');
		}
		
		
	},
});
