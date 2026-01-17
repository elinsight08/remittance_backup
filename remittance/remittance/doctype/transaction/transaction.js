// Copyright (c) 2025, Tafadzwa Barwa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transaction", {

    // Called after a document is saved (new or update)
    on_submit: function(frm) {
       console.log("Transaction saved:", frm.doc.name);
    },

    refresh(frm) {
        if (frm.doc.transaction_status === 'Completed') {
            frm.add_custom_button(__('Print'), () => {
                // const base_url = window.location.origin;
                // const url = `${base_url}/printview?doctype=Transaction&name=${frm.doc.name}&trigger_print=1&format=Recipient%20A4%20Receipt&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en`;
                // window.open(url, '_blank');
                openCustomPrint({
                    doctype: frm.doctype,
                    docname: frm.doc.name,
                    format: 'Recipient A4 Receipt',
                    letterhead: 'No Letterhead'
                });
            }).addClass('btn btn-primary');
        }
        if (frm.doc.docstatus === 1 && frm.doc.transaction_status === 'Pending' && frm.doc.owner === frappe.session.user) {
            frm.add_custom_button(__('Print'), () => {
                openCustomPrint({
                    doctype: frm.doctype,
                    docname: frm.doc.name,
                    format: 'Sender A4 Receipt',
                    letterhead: 'No Letterhead'
                });
            }).addClass('btn btn-primary');
        }

        if (frm.doc.docstatus === 1 && frm.doc.transaction_status === 'Reversed') {
            frm.add_custom_button(__('Print'), () => {
                openCustomPrint({
                    doctype: frm.doctype,
                    docname: frm.doc.name,
                    format: 'Reversal Receipt',
                    letterhead: 'No Letterhead'
                });
            }).addClass('btn btn-primary');
        }


        // filters reciptients with sender id
        if (frm.doc.docstatus === 1) {
            frm.set_df_property('charge', 'hidden', 1);
            frm.set_df_property('amount', 'hidden', 1);
        }

        frm.set_query('recipient_id', function () {
            return {
                filters: {
                    sender_id: frm.doc.customer
                }
            };
        });


        if (frm.doc.docstatus === 1 && frm.doc.transaction_status === 'Pending Reversal') { // Show button only for submitted documents

            frm.add_custom_button(__('Withdraw'), function () {
                // Show confirmation dialog first
                frappe.confirm(
                    __('Are you sure you want to withdraw this transaction?'),
                    function () {  // Yes
                        // Proceed with withdrawal after confirmation
                        frappe.call({
                            method: 'remittance.remittance.doctype.transaction.transaction.withdraw_reversal',
                            args: { docname: frm.doc.name, trans_status: "Reversed" },
                            freeze: true,
                            freeze_message: __('Processing Withdrawal...'),
                            callback: function (r) {
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
                                        message: __('Withdrawal Successful'),
                                        indicator: 'green'
                                    }, 5);
                                });
                            }
                        });
                    },
                    function () {  // No
                        // Cancel action
                        frappe.show_alert(__('Withdrawal Cancelled'), 3);
                    }
                );
            }).addClass('custom-withdraw-btn');
        }


        if (frm.doc.docstatus === 1 && frm.doc.transaction_status === 'Pending') { // Show button only for submitted documents

            frm.add_custom_button(__('Withdraw'), function () {
                // Show confirmation dialog first
                frappe.confirm(
                    __('Are you sure you want to withdraw this transaction?'),
                    function () {  // Yes
                        // Proceed with withdrawal after confirmation
                        frappe.call({
                            method: 'remittance.remittance.doctype.transaction.transaction.withdraw',
                            args: { docname: frm.doc.name },
                            freeze: true,
                            freeze_message: __('Processing Withdrawal...'),
                            callback: function (r) {
                                if (r.exc) {
                                    frappe.msgprint({
                                        title: __('Error'),
                                        indicator: 'red',
                                        message: r.exc
                                    });
                                    return;
                                }
                                 //     // 👉 Trigger print after successful withdrawal
                                setTimeout(() => {
                                    openCustomPrint({
                                        doctype: frm.doctype,
                                        docname: frm.doc.name,
                                        format: 'Recipient A4 Receipt',
                                        letterhead: 'No Letterhead'
                                    });
                                }, 800); // wait ~0.8 second
                                // Force refresh from server
                                frm.reload_doc(true, () => {
                                    console.log("Withdrawal ____________-response:", r.message);
                                    frappe.show_alert({
                                        message: __('Withdrawal Successful'),
                                        indicator: 'green'
                                    }, 5);


                                });


                            }
                        });
                    },
                    function () {  // No
                        // Cancel action
                        frappe.show_alert(__('Withdrawal Cancelled'), 3);
                    }
                );
            }).addClass('custom-withdraw-btn');
            frm.add_custom_button(__('Reverse Transaction'), function () {
                const dialog = new frappe.ui.Dialog({
                    title: __('Confirm Reversal'),
                    fields: [
                        {
                            fieldname: 'reversal_reason',
                            label: __('Reason for Reversal'),
                            fieldtype: 'Small Text',
                            reqd: 1
                        },
                        {
                            fieldname: 'confirm_checkbox',
                            label: __('Reverse with Charges'),
                            fieldtype: 'Check',
                            reqd: 0
                        }
                    ],
                    primary_action_label: __('Yes, Reverse'),
                    primary_action(values) {

                        // Call the server method after checkbox confirmation
                        frappe.call({
                            method: 'remittance.remittance.doctype.transaction.transaction.reverse_transaction',
                            args: { docname: frm.doc.name, reason: values.reversal_reason, apply_fee: values.confirm_checkbox },
                            freeze: true,
                            freeze_message: __('Processing Reversal...'),
                            callback: function (r) {
                                console.log("Response:", r.message);
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __('Reverse Successful'),
                                        indicator: 'green'
                                    }, 5);
                                }

                                frm.reload_doc(true, () => {
                                    frappe.show_alert({
                                        message: __('Reverse Successful'),
                                        indicator: 'green'
                                    }, 5);
                                    frm.reload_doc();
                                });
                            }
                        });

                        dialog.hide();
                    },
                    secondary_action_label: __('Cancel'),
                    secondary_action() {
                        frappe.show_alert(__('Reverse Cancelled'), 3);
                        dialog.hide();
                    }
                });

                dialog.show();
            }).addClass('btn-custom-reversal-btn'); // Add under the "Reports" menu
        }

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Update Recipient'), function () {
                showPromptDialog(frm);
            }).addClass('btn tf-daily-reconciliation-btn');
        }


    },
    receiver_amount: function (frm) {
        // Call the server-side function to get the charge
        frappe.call({
            method: "remittance.remittance.doctype.transaction.transaction.calculate_fee",  // Replace with your actual module path
            args: {
                receiver_amount: frm.doc.receiver_amount

            },

            callback: function (r) {
                if (r.message) {
                    console.log("Calculated charge:", r.message);
                    frm.set_value('charge', Math.ceil(r.message));
                    // Now that charge is updated, trigger total_amount calculation
                    frm.trigger('charge'); // Trigger the charge field's change event
                } else {
                    frm.set_value('charge', 0); // Or handle the error
                }
            }
        });
    },
    amount: function (frm) {
        // Call the server-side function to get the charge
        frappe.call({
            method: "remittance.remittance.doctype.transaction.transaction.calculate_receiver_fee",  // Replace with your actual module path
            args: {
                amount: frm.doc.amount

            },

            callback: function (r) {
                if (r.message) {
                    console.log("Calculated charge:", r.message);
                    frm.set_value('charge', Math.ceil(r.message));
                    // Now that charge is updated, trigger total_amount calculation
                    frm.trigger('charge'); // Trigger the charge field's change event
                } else {
                    frm.set_value('charge', 0); // Or handle the error
                }
            }
        });
    },
    charge: function (frm) {
        // Calculate total_amount whenever charge changes
        if (frm.doc.amount && frm.doc.charge) {
            totalAmount = frm.doc.amount - frm.doc.charge

            frm.set_value('receiver_amount', Math.ceil(totalAmount));


        }
        else if (frm.doc.receiver_amount && frm.doc.charge) {
            totalAmount = frm.doc.receiver_amount + frm.doc.charge

            frm.set_value('amount', Math.ceil(totalAmount));
        }


    }

});

function openCustomPrint({
    doctype,
    docname,
    format = 'Standard',
    letterhead = 'No Letterhead',
    no_letterhead = 1,
    hostname = window.location.origin,
    lang = 'en'
}) {
    const encodedFormat = encodeURIComponent(format);
    const encodedLetterhead = encodeURIComponent(letterhead);
    const url = `${hostname}/printview?doctype=${doctype}&name=${docname}&trigger_print=1&format=${encodedFormat}&no_letterhead=${no_letterhead}&letterhead=${encodedLetterhead}&settings=%7B%7D&_lang=${lang}`;
    window.open(url, '_blank');
}

function showPromptDialog(frm) {
    // Create dialog
    let dialog = new frappe.ui.Dialog({
        title: __('Enter Information'),
        fields: [
            {
                label: __('National ID'),
                fieldname: 'national_id',
                fieldtype: 'Data',
                reqd: 1,
                description: __('Enter the recipient national identification number'),
                validator: function (value) {

                    if (value.national_id === frm.doc.receiver_id) {
                        return __('New ID must be different from current ID');
                    }
                    return true;
                }
            }
        ],
        primary_action_label: __('Update'),
        primary_action(values) {
            // Call backend to update the document
            frappe.call({
                method: 'remittance.remittance.doctype.transaction.transaction.update_recipient_national_id',
                args: {
                    'transaction_name': frm.doc.name,
                    'national_id': values.national_id,
                    'recipient_id': frm.doc.recipient_id,
                    'mobile_no': frm.doc.mobile_no
                },
                callback: function (r) {
                    if (!r.exc) {
                        // Update the form with the new value
                        frm.set_value('national_id', values.national_id);
                    }
                    frm.reload_doc(true, () => {
                        frappe.show_alert({
                            message: __('National ID updated successfully'),
                            indicator: 'green'
                        }, 5);
                        frm.reload_doc();
                    });
                },
                freeze: true,
                freeze_message: __('Updating National ID...')
            });
            dialog.hide();
        }
    });

    dialog.show();
}
