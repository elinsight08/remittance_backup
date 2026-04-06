import json
import re
import frappe
from frappe.utils.xlsxutils import make_xlsx
from frappe.desk.utils import provide_binary_file

TRANS_REF_RE = re.compile(r"Trans Ref (TC\d+)")


@frappe.whitelist()
def export_sms_log_excel(filters=None):
    if filters and isinstance(filters, str):
        filters = json.loads(filters)

    records = frappe.get_all(
        "SMS Log",
        fields=["name", "creation", "sender_name", "sent_on", "message", "no_of_requested_sms", "no_of_sent_sms", "requested_numbers", "sent_to"],
        filters=filters or {},
        order_by="sent_on desc",
    )

    rows = [["Reference", "Created On", "Sender Name", "Sent On", "Message", "Transaction ID", "Requested SMS", "Sent SMS", "Requested Numbers", "Sent To"]]
    for d in records:
        message = d.message or ""
        if "has collected USD" not in message:
            continue
        match = TRANS_REF_RE.search(message)
        transaction_id = match.group(1) if match else ""
        rows.append([
            d.name,
            str(d.creation) if d.creation else "",
            d.sender_name,
            str(d.sent_on) if d.sent_on else "",
            message,
            transaction_id,
            d.no_of_requested_sms,
            d.no_of_sent_sms,
            d.requested_numbers,
            d.sent_to,
        ])

    xlsx_content = make_xlsx(rows, "SMS Log").getvalue()
    provide_binary_file("SMS Log", "xlsx", xlsx_content)


@frappe.whitelist()
def update_withdrawn_date_from_sms_log():
    """
    Query SMS Log directly for messages containing 'has collected USD',
    extract the Transaction ID (TCXXXXXX) and use the SMS Log creation
    date to update Transaction.withdrawn_date.
    """
    records = frappe.db.sql(
        """
        SELECT name, creation, message
        FROM `tabSMS Log`
        WHERE message LIKE %s
        """,
        ("%has collected USD%",),
        as_dict=True,
    )

    updated = []
    skipped = []

    for d in records:
        match = TRANS_REF_RE.search(d.message or "")
        if not match:
            skipped.append({"sms_log": d.name, "reason": "no transaction id found"})
            continue

        transaction_id = match.group(1)

        if not frappe.db.exists("Transaction", transaction_id):
            skipped.append({"sms_log": d.name, "reason": f"{transaction_id} not found"})
            continue

        frappe.db.sql(
            "UPDATE `tabTransaction` SET withdrawn_date = %s WHERE name = %s",
            (d.creation, transaction_id),
        )
        updated.append(transaction_id)

    frappe.db.commit()

    return {
        "updated": updated,
        "updated_count": len(updated),
        "skipped": skipped,
        "skipped_count": len(skipped),
    }



#frappe.call("remittance.remittance.data.ai.update_withdrawn_date_from_sms_log")
