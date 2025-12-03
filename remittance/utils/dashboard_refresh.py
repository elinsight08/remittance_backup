# remittance/utils/dashboard_refresh.py
import frappe
from frappe.realtime import emit_via_redis

def notify_dashboard_update(doc, method):
    """Notify all connected clients to refresh dashboard when transactions change"""
    try:
        # Only notify for relevant doctypes that affect dashboard
        relevant_doctypes = ['Transaction', 'Till Reconciliation']

        if doc.doctype in relevant_doctypes:
            # Emit real-time event to refresh dashboard
            emit_via_redis(
                event='dashboard_refresh',
                message={
                    'doctype': doc.doctype,
                    'action': method,
                    'timestamp': frappe.utils.now(),
                    'name': doc.name
                },
                room='dashboard_users'
            )

            # Also emit to all users (you can make this more specific)
            frappe.publish_realtime(
                event='dashboard_refresh',
                message={
                    'doctype': doc.doctype,
                    'action': method,
                    'timestamp': frappe.utils.now()
                }
            )

    except Exception as e:
        # Log error but don't break the main transaction
        frappe.log_error(f"Dashboard refresh notification failed: {str(e)}", "Dashboard Refresh Error")

@frappe.whitelist()
def force_refresh_all_dashboards():
    """Method to manually trigger dashboard refresh for all users"""
    try:
        frappe.publish_realtime(
            event='dashboard_refresh',
            message={
                'doctype': 'Manual Refresh',
                'action': 'force_refresh',
                'timestamp': frappe.utils.now()
            }
        )
        return {"status": "success", "message": "Dashboard refresh triggered for all users"}
    except Exception as e:
        frappe.log_error(f"Force dashboard refresh failed: {str(e)}")
        return {"status": "error", "message": str(e)}
