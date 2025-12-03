import frappe
from frappe.utils import nowdate, add_days
from frappe.core.doctype.sms_settings.sms_settings import send_sms

def _send_sms(mobile_no, msg):
        receiver_list = [mobile_no]
        if mobile_no:
            send_sms(receiver_list, msg)

def send_uncollected_fund_reminders_receiptient():
    settings = frappe.get_single('Uncollected Funds Reminder Settings')

    if not settings.is_enabled:
        return
    recipient_days = int(settings.recipient_reminder_days or 7)
    today = frappe.utils.nowdate()
    # Remind Recipients
    recipient_cutoff = add_days(today, -recipient_days)
    recipient_funds = frappe.get_all('Transaction', filters={
        'transaction_status': "Pending",
        'posting_date': ['<=', recipient_cutoff]
    }, fields=['name', 'sender_name', 'mobile_no', 'receiver_amount', 'currency', 'receiver_name'])
    for fund in recipient_funds:
        msg = f"Dear {fund.receiver_name}, you have an uncollected fund of {fund.currency}${fund.receiver_amount} pending since {recipient_cutoff}. Please collect it at your earliest convenience."
        if fund.mobile_no:
            _send_sms(fund.mobile_no, msg)


def send_uncollected_fund_reminders_sender():
    settings = frappe.get_single('Uncollected Funds Reminder Settings')

    if not settings.is_enabled:
        return
    sender_days = int(settings.sender_reminder_days or 30)
    today = frappe.utils.nowdate()

    # Remind Senders
    sender_cutoff = add_days(today, -sender_days)
    sender_funds = frappe.get_all('Transaction', filters={
        'transaction_status': "Pending",
        'posting_date': ['<=', sender_cutoff]
    }, fields=['name', 'sender_name', 'sender_mobile_no', 'receiver_amount', 'currency'])
    for fund in sender_funds:
        msg=f"Dear {fund.sender_name}, the fund (ID: {fund.name}) you sent has not been collected yet."
        if fund.sender_mobile_no:
            _send_sms(fund.sender_mobile_no, msg)

