app_name = "remittance"
app_title = "Remittance"
app_publisher = "Tafadzwa Barwa"
app_description = "Money transfer app"
app_email = "t.barwa95@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "remittance",
# 		"logo": "/assets/remittance/logo.png",
# 		"title": "Remittance",
# 		"route": "/remittance",
# 		"has_permission": "remittance.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/remittance/css/remittance.css"
# app_include_js = "/assets/remittance/js/remittance.js"

# include js, css files in header of web template
# web_include_css = "/assets/remittance/css/remittance.css"
# web_include_js = "/assets/remittance/js/remittance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "remittance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "remittance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "remittance.utils.jinja_methods",
# 	"filters": "remittance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "remittance.install.before_install"
# after_install = "remittance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "remittance.uninstall.before_uninstall"
# after_uninstall = "remittance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "remittance.utils.before_app_install"
# after_app_install = "remittance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "remittance.utils.before_app_uninstall"
# after_app_uninstall = "remittance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "remittance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Transaction": "remittance.permissions.permissions.transaction_permission_query"
}
#

# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
# doc_events = {
#     "CommissionConfiguration": {
#         "get_list": "remittance.remittancew.CommissionConfiguration.get_list"
#     }
# }
# override_doctype_class = {
#     "Transaction": "remittance.remittance.doctype.transaction.transaction.Transaction"
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"remittance.tasks.all"
	# ],
	"daily": [
		"remittance.utils.reminders.send_uncollected_fund_reminders_receiptient",
		"remittance.utils.reminders.send_uncollected_fund_reminders_sender"
	],
    "cron": {
        "0 2 * * *": [
            "remittance.utils.till_cron_tab.update_opening_balance_for_tills" # 0 2 * * * → means every day at 02:00 AM
        ]
    }
	# "hourly": [
	# 	"remittance.tasks.hourly"
	# ],
	# "weekly": [
	# 	"remittance.tasks.weekly"
	# ],
	# "monthly": [
	# 	"remittance.tasks.monthly"
	# ],
}

doc_events = {
    "Transaction": {
        "after_insert": "remittance.utils.dashboard_refresh.notify_dashboard_update",
        "after_update": "remittance.utils.dashboard_refresh.notify_dashboard_update",
        "on_cancel": "remittance.utils.dashboard_refresh.notify_dashboard_update"
    },
    "Till Reconciliation": {
        "after_insert": "remittance.utils.dashboard_refresh.notify_dashboard_update",
        "after_update": "remittance.utils.dashboard_refresh.notify_dashboard_update"
    }
    # Add other doctypes that should trigger dashboard refresh
}

# Testing
# -------

# before_tests = "remittance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "remittance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "remittance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["remittance.utils.before_request"]
# after_request = ["remittance.utils.after_request"]

# Job Events
# ----------
# before_job = ["remittance.utils.before_job"]
# after_job = ["remittance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"remittance.auth.validate"
# ]


# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }



